from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment, RawComment
from app.models.enums import (
    ClassificationStatus,
    ImportFormat,
    IngestionSourceType,
    IngestionStatus,
    MvpArea,
    NormalizationStatus,
    PrimaryCategory,
    SentimentLabel,
    SourcePlatform,
)
from app.models.ingestion import IngestionRun
from app.repositories.signals import SignalRepository
from app.services.dashboard import DashboardService


def _seed_comment(
    db_session,
    *,
    run: IngestionRun,
    source_comment_id: str,
    source_video_id: str | None,
    text: str,
    primary_category: PrimaryCategory,
    mvp_area: MvpArea,
    sentiment: SentimentLabel,
    confidence: float,
    relevance: float,
    urgency: float,
    comment_created_at: datetime | None = None,
    needs_review: bool = False,
):
    raw_comment = RawComment(
        id=uuid4(),
        ingestion_run_id=run.id,
        source_platform=SourcePlatform.TIKTOK,
        source_video_id=source_video_id,
        source_comment_id=source_comment_id,
        source_parent_comment_id=None,
        author_handle="tester",
        comment_text=text,
        comment_created_at=comment_created_at or datetime.now(UTC),
        like_count=0,
        reply_count=0,
        row_number=1,
        is_duplicate=False,
        raw_payload_json={"comment": text},
    )
    db_session.add(raw_comment)
    db_session.flush()

    normalized_comment = NormalizedComment(
        id=uuid4(),
        raw_comment_id=raw_comment.id,
        ingestion_run_id=run.id,
        source_platform=SourcePlatform.TIKTOK,
        source_video_id=source_video_id,
        source_comment_id=source_comment_id,
        source_parent_comment_id=None,
        author_handle="tester",
        original_text=text,
        normalized_text=text.lower(),
        comment_created_at=raw_comment.comment_created_at,
        like_count=0,
        reply_count=0,
        normalization_status=NormalizationStatus.NORMALIZED,
        classification_status=ClassificationStatus.NEEDS_REVIEW if needs_review else ClassificationStatus.CLASSIFIED,
        rules_matched=[],
    )
    db_session.add(normalized_comment)
    db_session.flush()

    classification = CommentClassification(
        id=uuid4(),
        normalized_comment_id=normalized_comment.id,
        normalized_comment=normalized_comment,
        provider="stub",
        model_name="stub",
        prompt_version="v1",
        raw_response={},
        primary_category=primary_category,
        secondary_categories=[],
        mvp_area=mvp_area,
        sentiment=sentiment,
        confidence=confidence,
        mvp_relevance_score=relevance,
        urgency_score=urgency,
        needs_human_review=needs_review,
        recommended_action="Review the evidence.",
        rationale_short="Seeded for dashboard insight coverage.",
        review_status=ClassificationStatus.NEEDS_REVIEW if needs_review else ClassificationStatus.CLASSIFIED,
        reviewer_note=None,
        reviewed_at=None,
        override_primary_category=None,
        override_mvp_area=None,
        is_false_positive=False,
    )
    db_session.add(classification)
    db_session.flush()


def test_dashboard_audience_insights_surface_story_driven_mvp_themes(db_session):
    run = IngestionRun(
        source_type=IngestionSourceType.JSON_UPLOAD,
        source_platform=SourcePlatform.TIKTOK,
        import_format=ImportFormat.PORTABILITY_JSON,
        source_label="audience.json",
        status=IngestionStatus.IMPORTED,
        total_rows=4,
        imported_rows=4,
        duplicate_rows=0,
        failed_rows=0,
        run_metadata={},
    )
    db_session.add(run)
    db_session.flush()

    _seed_comment(
        db_session,
        run=run,
        source_comment_id="comment-1",
        source_video_id="video-1",
        text="Need same day meetup coordination for solo friends",
        primary_category=PrimaryCategory.SOCIAL_COORDINATION,
        mvp_area=MvpArea.MEETUPS,
        sentiment=SentimentLabel.NEUTRAL,
        confidence=0.83,
        relevance=0.91,
        urgency=0.72,
    )
    _seed_comment(
        db_session,
        run=run,
        source_comment_id="comment-2",
        source_video_id="video-1",
        text="Please add report user flow and fake profile checks for safety",
        primary_category=PrimaryCategory.SAFETY_OR_TRUST,
        mvp_area=MvpArea.SAFETY,
        sentiment=SentimentLabel.NEGATIVE,
        confidence=0.9,
        relevance=0.94,
        urgency=0.93,
        needs_review=True,
    )
    _seed_comment(
        db_session,
        run=run,
        source_comment_id="comment-3",
        source_video_id=None,
        text="I am confused how beta signup works for dating mode",
        primary_category=PrimaryCategory.CONFUSION_OR_ONBOARDING,
        mvp_area=MvpArea.ONBOARDING,
        sentiment=SentimentLabel.NEUTRAL,
        confidence=0.79,
        relevance=0.86,
        urgency=0.68,
        needs_review=True,
    )
    _seed_comment(
        db_session,
        run=run,
        source_comment_id="comment-4",
        source_video_id="video-2",
        text="Love this idea for friendship mode in theme parks",
        primary_category=PrimaryCategory.PRAISE_OR_DELIGHT,
        mvp_area=MvpArea.COMMUNITY,
        sentiment=SentimentLabel.POSITIVE,
        confidence=0.8,
        relevance=0.76,
        urgency=0.55,
    )
    db_session.commit()

    service = DashboardService(db_session, SignalRepository(db_session))
    insights = service.get_audience_insights()
    summary = service.get_summary()

    assert any(item.key == "safety_and_moderation" for item in insights.mvp_priorities)
    assert any(item.key == "friendship_mode" for item in insights.story_alignment)
    assert any(item.key == "beta_and_onboarding" for item in insights.confusion_points)
    assert insights.top_videos[0].label == "video-1"
    assert summary.earliest_comment_date is not None
    assert summary.latest_comment_date is not None
    assert summary.months_represented >= 1
    assert any(item.key == "Safety & Moderation" for item in summary.top_user_concerns)


def test_dashboard_trends_cover_full_imported_date_span(db_session):
    run = IngestionRun(
        source_type=IngestionSourceType.JSON_UPLOAD,
        source_platform=SourcePlatform.TIKTOK,
        import_format=ImportFormat.PORTABILITY_JSON,
        source_label="span.json",
        status=IngestionStatus.IMPORTED,
        total_rows=3,
        imported_rows=3,
        duplicate_rows=0,
        failed_rows=0,
        run_metadata={},
    )
    db_session.add(run)
    db_session.flush()

    _seed_comment(
        db_session,
        run=run,
        source_comment_id="span-1",
        source_video_id="video-1",
        text="July comment",
        primary_category=PrimaryCategory.FEATURE_REQUEST,
        mvp_area=MvpArea.MATCHING,
        sentiment=SentimentLabel.NEUTRAL,
        confidence=0.8,
        relevance=0.8,
        urgency=0.6,
        comment_created_at=datetime(2025, 7, 8, 11, 22, 2, tzinfo=UTC),
    )
    _seed_comment(
        db_session,
        run=run,
        source_comment_id="span-2",
        source_video_id="video-1",
        text="October comment",
        primary_category=PrimaryCategory.SOCIAL_COORDINATION,
        mvp_area=MvpArea.MEETUPS,
        sentiment=SentimentLabel.NEUTRAL,
        confidence=0.8,
        relevance=0.8,
        urgency=0.6,
        comment_created_at=datetime(2025, 10, 1, 9, 0, 0, tzinfo=UTC),
        needs_review=True,
    )
    _seed_comment(
        db_session,
        run=run,
        source_comment_id="span-3",
        source_video_id="video-2",
        text="March comment",
        primary_category=PrimaryCategory.PRAISE_OR_DELIGHT,
        mvp_area=MvpArea.COMMUNITY,
        sentiment=SentimentLabel.POSITIVE,
        confidence=0.8,
        relevance=0.8,
        urgency=0.6,
        comment_created_at=datetime(2026, 3, 7, 22, 36, 43, tzinfo=UTC),
    )
    db_session.commit()

    service = DashboardService(db_session, SignalRepository(db_session))
    summary = service.get_summary()
    trends = service.get_trends()

    assert str(summary.earliest_comment_date).startswith("2025-07-08")
    assert str(summary.latest_comment_date).startswith("2026-03-07")
    assert summary.months_represented == 3
    assert trends[0].bucket == "2025-07"
    assert trends[-1].bucket == "2026-03"
    assert any(point.bucket == "2025-10" and point.review_queue == 1 for point in trends)
