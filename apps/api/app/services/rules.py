from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import MvpArea, PrimaryCategory


class RuleEvaluation(BaseModel):
    tags: list[str] = Field(default_factory=list)
    primary_category: PrimaryCategory | None = None
    mvp_area: MvpArea | None = None
    needs_human_review: bool = False
    urgency_floor: float = 0.0
    relevance_floor: float = 0.0
    confidence_floor: float = 0.0
    recommended_action: str | None = None
    short_circuit: bool = False


RULE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "tag": "safety",
        "terms": ["safety"],
        "primary_category": PrimaryCategory.SAFETY_OR_TRUST,
        "mvp_area": MvpArea.SAFETY,
        "needs_human_review": True,
        "urgency_floor": 0.9,
        "relevance_floor": 0.9,
        "confidence_floor": 0.92,
        "recommended_action": "Review safety and trust policy gaps.",
        "short_circuit": True,
    },
    {
        "tag": "fake",
        "terms": ["fake"],
        "primary_category": PrimaryCategory.MODERATION_OR_BOT,
        "mvp_area": MvpArea.MODERATION,
        "needs_human_review": True,
        "urgency_floor": 0.88,
        "relevance_floor": 0.88,
        "confidence_floor": 0.9,
        "recommended_action": "Investigate fake profile and trust tooling needs.",
        "short_circuit": True,
    },
    {
        "tag": "bot",
        "terms": ["bot", "bots"],
        "primary_category": PrimaryCategory.MODERATION_OR_BOT,
        "mvp_area": MvpArea.MODERATION,
        "needs_human_review": True,
        "urgency_floor": 0.86,
        "relevance_floor": 0.84,
        "confidence_floor": 0.88,
        "recommended_action": "Strengthen bot detection and moderation workflows.",
        "short_circuit": True,
    },
    {
        "tag": "meetup",
        "terms": ["meetup", "meet ups", "same day"],
        "primary_category": PrimaryCategory.SOCIAL_COORDINATION,
        "mvp_area": MvpArea.MEETUPS,
        "needs_human_review": False,
        "urgency_floor": 0.72,
        "relevance_floor": 0.86,
        "confidence_floor": 0.82,
        "recommended_action": "Consider meetup coordination and same-day planning support.",
        "short_circuit": True,
    },
    {
        "tag": "beta",
        "terms": ["beta"],
        "primary_category": PrimaryCategory.FEATURE_REQUEST,
        "mvp_area": MvpArea.ONBOARDING,
        "needs_human_review": False,
        "urgency_floor": 0.58,
        "relevance_floor": 0.78,
        "confidence_floor": 0.74,
        "recommended_action": "Track beta access demand and onboarding waitlist needs.",
        "short_circuit": False,
    },
    {
        "tag": "passholder",
        "terms": ["passholder", "annual pass"],
        "primary_category": PrimaryCategory.PRICING_OR_VALUE,
        "mvp_area": MvpArea.PASSHOLDERS,
        "needs_human_review": False,
        "urgency_floor": 0.62,
        "relevance_floor": 0.8,
        "confidence_floor": 0.78,
        "recommended_action": "Evaluate passholder-specific features or pricing bundles.",
        "short_circuit": True,
    },
]


class KeywordRuleService:
    """Simple deterministic keyword pre-pass before LLM classification."""

    def evaluate(self, text: str) -> RuleEvaluation:
        lowered = text.lower()
        result = RuleEvaluation()

        for rule in RULE_DEFINITIONS:
            if any(term in lowered for term in rule["terms"]):
                result.tags.append(rule["tag"])
                result.primary_category = result.primary_category or rule["primary_category"]
                result.mvp_area = result.mvp_area or rule["mvp_area"]
                result.needs_human_review = result.needs_human_review or rule["needs_human_review"]
                result.urgency_floor = max(result.urgency_floor, rule["urgency_floor"])
                result.relevance_floor = max(result.relevance_floor, rule["relevance_floor"])
                result.confidence_floor = max(result.confidence_floor, rule["confidence_floor"])
                result.recommended_action = result.recommended_action or rule["recommended_action"]
                result.short_circuit = result.short_circuit or rule["short_circuit"]

        return result
