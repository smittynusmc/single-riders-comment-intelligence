from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment
from app.models.enums import ClassificationStatus, MvpArea, PrimaryCategory, SentimentLabel
from app.prompts import CLASSIFICATION_PROMPT_VERSION, build_classification_messages
from app.repositories.classifications import ClassificationRepository
from app.repositories.comments import CommentRepository
from app.schemas.classifications import ClassificationResultPayload
from app.services.rules import KeywordRuleService, RuleEvaluation

settings = get_settings()


class ClassificationResultParser:
    """Parses model output into the strict classification schema."""

    def parse(self, payload: dict[str, Any] | str) -> ClassificationResultPayload:
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = dict(payload)

        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            data = json.loads(content)

        for key in ("confidence", "mvp_relevance_score", "urgency_score"):
            data[key] = max(0.0, min(1.0, float(data[key])))

        if not isinstance(data.get("secondary_categories", []), list):
            data["secondary_categories"] = [str(data["secondary_categories"])]

        return ClassificationResultPayload.model_validate(data)


class BaseClassifierClient(ABC):
    provider_name: str

    @abstractmethod
    def classify(self, *, comment_text: str, rules: RuleEvaluation) -> dict[str, Any] | str:
        """Return a JSON payload or JSON string matching the classification schema."""


class StubLLMClassifierClient(BaseClassifierClient):
    provider_name = "stub"

    def classify(self, *, comment_text: str, rules: RuleEvaluation) -> dict[str, Any]:
        lowered = comment_text.lower()
        primary_category = rules.primary_category or self._infer_primary_category(lowered)
        mvp_area = rules.mvp_area or self._infer_mvp_area(lowered)
        sentiment = self._infer_sentiment(lowered)
        confidence = max(rules.confidence_floor, 0.7 if rules.tags else 0.62)
        relevance = max(rules.relevance_floor, 0.65)
        urgency = max(rules.urgency_floor, 0.45)
        needs_review = rules.needs_human_review or ("?" in comment_text and confidence < 0.7)
        recommended_action = rules.recommended_action or self._recommended_action(primary_category, mvp_area)
        secondary = list(dict.fromkeys(rules.tags + [primary_category.value]))[:3]

        return {
            "primary_category": primary_category.value,
            "secondary_categories": secondary,
            "mvp_area": mvp_area.value,
            "sentiment": sentiment.value,
            "confidence": confidence,
            "mvp_relevance_score": relevance,
            "urgency_score": urgency,
            "needs_human_review": needs_review,
            "recommended_action": recommended_action,
            "rationale_short": f"Heuristic classification based on rules and comment wording.",
        }

    def _infer_primary_category(self, lowered: str) -> PrimaryCategory:
        if any(term in lowered for term in ["bug", "broken", "glitch", "crash", "error"]):
            return PrimaryCategory.BUG_OR_QUALITY
        if any(term in lowered for term in ["safe", "unsafe", "creepy"]):
            return PrimaryCategory.SAFETY_OR_TRUST
        if any(term in lowered for term in ["how", "confused", "what does", "where do i"]):
            return PrimaryCategory.CONFUSION_OR_ONBOARDING
        if any(term in lowered for term in ["love", "cute", "great", "amazing"]):
            return PrimaryCategory.PRAISE_OR_DELIGHT
        if any(term in lowered for term in ["price", "cost", "worth", "pay"]):
            return PrimaryCategory.PRICING_OR_VALUE
        if any(term in lowered for term in ["meet", "group", "same day", "hang"]):
            return PrimaryCategory.SOCIAL_COORDINATION
        return PrimaryCategory.FEATURE_REQUEST

    def _infer_mvp_area(self, lowered: str) -> MvpArea:
        if any(term in lowered for term in ["profile", "bio", "photo"]):
            return MvpArea.PROFILES
        if any(term in lowered for term in ["message", "chat", "dm"]):
            return MvpArea.MESSAGING
        if any(term in lowered for term in ["safe", "unsafe", "creepy"]):
            return MvpArea.SAFETY
        if any(term in lowered for term in ["meet", "same day", "hang"]):
            return MvpArea.MEETUPS
        if any(term in lowered for term in ["passholder", "annual pass"]):
            return MvpArea.PASSHOLDERS
        if any(term in lowered for term in ["moderation", "bot", "fake"]):
            return MvpArea.MODERATION
        if any(term in lowered for term in ["onboard", "beta", "waitlist"]):
            return MvpArea.ONBOARDING
        return MvpArea.MATCHING

    def _infer_sentiment(self, lowered: str) -> SentimentLabel:
        if any(term in lowered for term in ["love", "great", "amazing", "fun"]):
            return SentimentLabel.POSITIVE
        if any(term in lowered for term in ["hate", "bad", "broken", "unsafe", "fake"]):
            return SentimentLabel.NEGATIVE
        if "but" in lowered:
            return SentimentLabel.MIXED
        return SentimentLabel.NEUTRAL

    def _recommended_action(self, category: PrimaryCategory, mvp_area: MvpArea) -> str:
        if category == PrimaryCategory.BUG_OR_QUALITY:
            return "Confirm the issue and scope a product quality fix."
        if category == PrimaryCategory.SOCIAL_COORDINATION:
            return "Explore a coordination workflow for park-day meetups."
        if category == PrimaryCategory.SAFETY_OR_TRUST:
            return "Review safety and trust safeguards before broader rollout."
        return f"Review demand for {mvp_area.value.replace('_', ' ')} improvements."


class OpenAICompatibleClassifierClient(BaseClassifierClient):
    provider_name = "openai_compatible"

    def __init__(self, *, base_url: str, model_name: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key

    def classify(self, *, comment_text: str, rules: RuleEvaluation) -> dict[str, Any] | str:
        if not self.base_url:
            raise ValueError("SCI_LLM_BASE_URL is required for the openai_compatible provider.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": build_classification_messages(comment_text=comment_text, rules=rules),
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()


class CommentClassificationService:
    """Runs rules plus a configurable classifier and persists structured outputs."""

    def __init__(
        self,
        *,
        comment_repository: CommentRepository,
        classification_repository: ClassificationRepository,
        rule_service: KeywordRuleService,
        parser: ClassificationResultParser | None = None,
    ):
        self.comment_repository = comment_repository
        self.classification_repository = classification_repository
        self.rule_service = rule_service
        self.parser = parser or ClassificationResultParser()
        self.stub_client = StubLLMClassifierClient()

    def classify_comments(self, comments: list[NormalizedComment]) -> list[CommentClassification]:
        classifications: list[CommentClassification] = []
        for comment in comments:
            classifications.append(self.classify_comment(comment))
        return classifications

    def classify_comment(self, comment: NormalizedComment) -> CommentClassification:
        rules = self.rule_service.evaluate(comment.normalized_text)
        client = self._build_client()

        if rules.short_circuit:
            raw_output = self.stub_client.classify(comment_text=comment.normalized_text, rules=rules)
            provider_name = "rules_short_circuit"
            model_name = settings.llm_model
        else:
            raw_output = client.classify(comment_text=comment.normalized_text, rules=rules)
            provider_name = client.provider_name
            model_name = settings.llm_model

        parsed = self._merge_rules(self.parser.parse(raw_output), rules)
        review_status = ClassificationStatus.NEEDS_REVIEW if parsed.needs_human_review else ClassificationStatus.CLASSIFIED

        classification = self.classification_repository.upsert(
            normalized_comment=comment,
            values={
                "provider": provider_name,
                "model_name": model_name,
                "prompt_version": CLASSIFICATION_PROMPT_VERSION,
                "raw_response": raw_output if isinstance(raw_output, dict) else {"content": raw_output},
                "primary_category": parsed.primary_category,
                "secondary_categories": parsed.secondary_categories,
                "mvp_area": parsed.mvp_area,
                "sentiment": parsed.sentiment,
                "confidence": parsed.confidence,
                "mvp_relevance_score": parsed.mvp_relevance_score,
                "urgency_score": parsed.urgency_score,
                "needs_human_review": parsed.needs_human_review,
                "recommended_action": parsed.recommended_action,
                "rationale_short": parsed.rationale_short,
                "review_status": review_status,
            },
        )
        self.comment_repository.update_classification_status(comment, review_status)
        return classification

    def _build_client(self) -> BaseClassifierClient:
        if settings.llm_provider == "stub":
            return self.stub_client
        if settings.llm_provider == "openai_compatible":
            return OpenAICompatibleClassifierClient(
                base_url=settings.llm_base_url or "",
                model_name=settings.llm_model,
                api_key=settings.llm_api_key,
            )
        raise ValueError(f"Unsupported classifier provider: {settings.llm_provider}")

    def _merge_rules(self, parsed: ClassificationResultPayload, rules: RuleEvaluation) -> ClassificationResultPayload:
        data = parsed.model_dump()
        if rules.primary_category:
            data["primary_category"] = rules.primary_category
        if rules.mvp_area:
            data["mvp_area"] = rules.mvp_area
        data["confidence"] = max(float(data["confidence"]), rules.confidence_floor)
        data["mvp_relevance_score"] = max(float(data["mvp_relevance_score"]), rules.relevance_floor)
        data["urgency_score"] = max(float(data["urgency_score"]), rules.urgency_floor)
        data["needs_human_review"] = bool(data["needs_human_review"] or rules.needs_human_review)
        if rules.recommended_action and float(data["confidence"]) < 0.85:
            data["recommended_action"] = rules.recommended_action
        data["secondary_categories"] = list(dict.fromkeys(list(data["secondary_categories"]) + rules.tags))
        return ClassificationResultPayload.model_validate(data)
