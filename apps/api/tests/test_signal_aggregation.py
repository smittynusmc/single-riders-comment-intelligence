from __future__ import annotations

from uuid import uuid4

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment
from app.models.enums import ClassificationStatus, MvpArea, NormalizationStatus, PrimaryCategory, SentimentLabel, SourcePlatform
from app.services.aggregation import SignalAggregationService


class StubClassificationRepository:
    def __init__(self, items):
        self._items = items

    def active_for_signal_build(self):
        return self._items


def build_classification(comment_text: str, *, relevance: float, urgency: float, confidence: float):
    normalized_comment = NormalizedComment(
        id=uuid4(),
        raw_comment_id=uuid4(),
        ingestion_run_id=uuid4(),
        source_platform=SourcePlatform.TIKTOK,
        source_video_id="video-1",
        source_comment_id=str(uuid4()),
        author_handle="tester",
        original_text=comment_text,
        normalized_text=comment_text.lower(),
        like_count=0,
        reply_count=0,
        normalization_status=NormalizationStatus.NORMALIZED,
        classification_status=ClassificationStatus.CLASSIFIED,
        rules_matched=["meetup"],
    )
    return CommentClassification(
        id=uuid4(),
        normalized_comment_id=normalized_comment.id,
        normalized_comment=normalized_comment,
        provider="stub",
        model_name="stub-model",
        prompt_version="v1",
        raw_response={},
        primary_category=PrimaryCategory.SOCIAL_COORDINATION,
        secondary_categories=["meetup"],
        mvp_area=MvpArea.MEETUPS,
        sentiment=SentimentLabel.NEUTRAL,
        confidence=confidence,
        mvp_relevance_score=relevance,
        urgency_score=urgency,
        needs_human_review=False,
        recommended_action="Build meetup planning.",
        rationale_short="Repeated meetup request.",
        review_status=ClassificationStatus.CLASSIFIED,
        is_false_positive=False,
    )


def test_signal_aggregation_priority_score_rewards_evidence_count():
    single = build_classification("Need meetup matching", relevance=0.8, urgency=0.7, confidence=0.75)
    repeated = [
        build_classification("Need meetup matching", relevance=0.8, urgency=0.7, confidence=0.75),
        build_classification("Same day meetup feature please", relevance=0.82, urgency=0.72, confidence=0.76),
        build_classification("Meetup coordination would help", relevance=0.81, urgency=0.71, confidence=0.78),
    ]

    service_single = SignalAggregationService(StubClassificationRepository([single]))
    service_repeated = SignalAggregationService(StubClassificationRepository(repeated))

    single_signals, _ = service_single.rebuild()
    repeated_signals, _ = service_repeated.rebuild()

    assert len(single_signals) == 1
    assert len(repeated_signals) == 1
    assert repeated_signals[0].priority_score > single_signals[0].priority_score
    assert repeated_signals[0].evidence_count == 3
