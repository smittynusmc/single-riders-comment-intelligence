from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.base  # noqa: F401
from app.api.deps import db_session
from app.main import app
from app.models.base import Base
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


def test_list_classifications_allows_null_source_video_id():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    session: Session = TestingSession()

    def override_db_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[db_session] = override_db_session

    try:
        run = IngestionRun(
            source_type=IngestionSourceType.JSON_UPLOAD,
            source_platform=SourcePlatform.TIKTOK,
            import_format=ImportFormat.PORTABILITY_JSON,
            source_label="portability.json",
            status=IngestionStatus.IMPORTED,
            total_rows=1,
            imported_rows=1,
            duplicate_rows=0,
            failed_rows=0,
            run_metadata={},
        )
        session.add(run)
        session.flush()

        raw_comment = RawComment(
            ingestion_run_id=run.id,
            source_platform=SourcePlatform.TIKTOK,
            source_video_id=None,
            source_comment_id="generated-123",
            source_parent_comment_id=None,
            author_handle=None,
            comment_text="Portability export comment",
            comment_created_at=None,
            like_count=0,
            reply_count=0,
            row_number=1,
            is_duplicate=False,
            raw_payload_json={"comment": "Portability export comment"},
        )
        session.add(raw_comment)
        session.flush()

        normalized_comment = NormalizedComment(
            raw_comment_id=raw_comment.id,
            ingestion_run_id=run.id,
            source_platform=SourcePlatform.TIKTOK,
            source_video_id=None,
            source_comment_id=raw_comment.source_comment_id,
            source_parent_comment_id=None,
            author_handle=None,
            original_text=raw_comment.comment_text,
            normalized_text=raw_comment.comment_text.lower(),
            comment_created_at=None,
            like_count=0,
            reply_count=0,
            normalization_status=NormalizationStatus.NORMALIZED,
            classification_status=ClassificationStatus.CLASSIFIED,
            rules_matched=[],
        )
        session.add(normalized_comment)
        session.flush()

        classification = CommentClassification(
            normalized_comment_id=normalized_comment.id,
            provider="stub",
            model_name="test-model",
            prompt_version="v1",
            raw_response={},
            primary_category=PrimaryCategory.SOCIAL_COORDINATION,
            secondary_categories=[],
            mvp_area=MvpArea.MEETUPS,
            sentiment=SentimentLabel.POSITIVE,
            confidence=0.91,
            mvp_relevance_score=0.88,
            urgency_score=0.42,
            needs_human_review=False,
            recommended_action="Review with product",
            rationale_short="Strong portability signal.",
            review_status=ClassificationStatus.CLASSIFIED,
            reviewer_note=None,
            reviewed_at=None,
            override_primary_category=None,
            override_mvp_area=None,
            is_false_positive=False,
        )
        session.add(classification)
        session.commit()

        with TestClient(app) as client:
            response = client.get("/classifications?limit=100")

        assert response.status_code == 200
        payload = response.json()
        assert payload["meta"]["total"] == 1
        assert payload["items"][0]["normalized_comment"]["source_video_id"] is None
        assert payload["items"][0]["classification"]["id"] == str(classification.id)
    finally:
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)
