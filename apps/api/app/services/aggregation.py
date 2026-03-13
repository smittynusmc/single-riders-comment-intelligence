from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from uuid import uuid4

from app.models.classification import CommentClassification
from app.models.enums import MvpArea, PrimaryCategory, SignalStatus
from app.models.signal import MvpSignal, SignalCommentLink
from app.repositories.classifications import ClassificationRepository

STOPWORDS = {
    "a", "an", "and", "be", "for", "i", "is", "it", "me", "my", "of", "on", "or", "so", "the", "this", "to", "we", "with", "you",
}
TOKEN_RE = re.compile(r"[a-z0-9]+")


class SignalAggregationService:
    """Groups classified comments into ranked MVP signals."""

    def __init__(self, classification_repository: ClassificationRepository):
        self.classification_repository = classification_repository

    def rebuild(self, existing_signals: dict[str, MvpSignal] | None = None) -> tuple[list[MvpSignal], list[SignalCommentLink]]:
        classifications = self.classification_repository.active_for_signal_build()
        grouped: dict[str, list[CommentClassification]] = defaultdict(list)
        existing_signals = existing_signals or {}

        for classification in classifications:
            effective_category = classification.override_primary_category or classification.primary_category
            effective_mvp_area = classification.override_mvp_area or classification.mvp_area
            fingerprint = self._build_group_fingerprint(
                text=classification.normalized_comment.normalized_text,
                rules=classification.normalized_comment.rules_matched,
                primary_category=effective_category,
                mvp_area=effective_mvp_area,
            )
            grouped[fingerprint].append(classification)

        signals: list[MvpSignal] = []
        links: list[SignalCommentLink] = []

        for fingerprint, group in grouped.items():
            primary_category = group[0].override_primary_category or group[0].primary_category
            mvp_area = group[0].override_mvp_area or group[0].mvp_area
            existing = existing_signals.get(fingerprint)
            signal_id = existing.id if existing else uuid4()
            sample_comments = [
                {
                    "comment_id": str(item.normalized_comment.id),
                    "text": item.normalized_comment.original_text,
                    "author_handle": item.normalized_comment.author_handle,
                }
                for item in group[:3]
            ]
            signal = MvpSignal(
                id=signal_id,
                fingerprint=fingerprint,
                title=self._build_title(group, mvp_area),
                summary=self._build_summary(group),
                mvp_area=mvp_area,
                primary_category=primary_category,
                status=existing.status if existing else SignalStatus.ACTIVE,
                evidence_count=len(group),
                priority_score=self._build_priority_score(group),
                first_seen_at=min(
                    (item.normalized_comment.comment_created_at or item.normalized_comment.created_at for item in group),
                    default=datetime.now(UTC),
                ),
                last_seen_at=max(
                    (item.normalized_comment.comment_created_at or item.normalized_comment.created_at for item in group),
                    default=datetime.now(UTC),
                ),
                sample_comments=sample_comments,
                suggested_backlog_action=group[0].recommended_action,
                reviewed_at=existing.reviewed_at if existing else None,
                reviewed_by=existing.reviewed_by if existing else None,
                export_metadata=dict(existing.export_metadata) if existing else {},
                created_at=existing.created_at if existing else datetime.now(UTC),
            )
            signals.append(signal)

            for item in group:
                links.append(
                    SignalCommentLink(
                        id=uuid4(),
                        signal_id=signal_id,
                        normalized_comment_id=item.normalized_comment_id,
                        classification_id=item.id,
                        relevance_score=item.mvp_relevance_score,
                    )
                )

        return signals, links

    def _build_group_fingerprint(
        self,
        *,
        text: str,
        rules: list[str],
        primary_category: PrimaryCategory,
        mvp_area: MvpArea,
    ) -> str:
        tokens = [token for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS]
        signature = sorted(dict.fromkeys((rules + tokens[:4])[:4]))
        if not signature:
            signature = ["general"]
        return f"{mvp_area.value}:{primary_category.value}:{'-'.join(signature)}"

    def _build_title(self, group: list[CommentClassification], mvp_area: MvpArea) -> str:
        keywords = Counter()
        for item in group:
            keywords.update(item.normalized_comment.rules_matched)
            keywords.update(token for token in TOKEN_RE.findall(item.normalized_comment.normalized_text) if token not in STOPWORDS)
        top_keyword = keywords.most_common(1)[0][0] if keywords else "feedback"
        return f"{mvp_area.value.replace('_', ' ').title()}: repeated {top_keyword} signal"

    def _build_summary(self, group: list[CommentClassification]) -> str:
        sample_texts = [item.normalized_comment.original_text for item in group[:2]]
        return (
            f"{len(group)} comments point to the same product signal. "
            f"Examples: {' | '.join(sample_texts)}"
        )

    def _build_priority_score(self, group: list[CommentClassification]) -> float:
        avg_relevance = sum(item.mvp_relevance_score for item in group) / len(group)
        avg_urgency = sum(item.urgency_score for item in group) / len(group)
        avg_confidence = sum(item.confidence for item in group) / len(group)
        evidence_boost = min(1.5, 1 + math.log(len(group) + 1, 10))
        return round(((avg_relevance * 0.45) + (avg_urgency * 0.35) + (avg_confidence * 0.2)) * 100 * evidence_boost, 2)
