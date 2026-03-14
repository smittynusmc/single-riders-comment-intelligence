from __future__ import annotations

from app.models.enums import ImportFormat
from app.repositories.classifications import ClassificationRepository
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.repositories.signals import SignalRepository
from app.services.aggregation import SignalAggregationService
from app.services.classification import ClassificationResultParser, CommentClassificationService
from app.services.import_service import ImportService
from app.services.normalization import NormalizationService
from app.services.pipeline import IngestionPipelineService
from app.services.rules import KeywordRuleService

MULTI_MONTH_JSON_CONTENT = b"""{
  "comments": [
    {
      "video_id": "video-1",
      "comment_id": "comment-july",
      "user": { "unique_id": "userone" },
      "text": "Need a meetup feature",
      "create_time": "2025-07-08T11:22:02Z",
      "digg_count": 10,
      "reply_comment_total": 2
    },
    {
      "video_id": "video-2",
      "comment_id": "comment-march",
      "user": { "unique_id": "usertwo" },
      "text": "Please add a bot filter",
      "create_time": "2026-03-07T22:36:43Z",
      "digg_count": 5,
      "reply_comment_total": 1
    }
  ]
}"""


def test_pipeline_audit_preserves_counts_across_normalization_and_classification(db_session):
    ingestion_repository = IngestionRunRepository(db_session)
    comment_repository = CommentRepository(db_session)
    import_service = ImportService(ingestion_repository, comment_repository)
    run = import_service.import_json_bytes(file_bytes=MULTI_MONTH_JSON_CONTENT, filename="multi-month-comments.json")
    db_session.commit()

    rule_service = KeywordRuleService()
    pipeline = IngestionPipelineService(
        ingestion_repository=ingestion_repository,
        normalization_service=NormalizationService(comment_repository, rule_service),
        classification_service=CommentClassificationService(
            comment_repository=comment_repository,
            classification_repository=ClassificationRepository(db_session),
            rule_service=rule_service,
            parser=ClassificationResultParser(),
        ),
        aggregation_service=SignalAggregationService(ClassificationRepository(db_session)),
        signal_repository=SignalRepository(db_session),
    )

    pipeline.process_run(run.id)
    db_session.commit()
    db_session.refresh(run)

    assert run.import_format == ImportFormat.TIKTOK_JSON
    audit = run.run_metadata["pipeline_audit"]
    assert audit["json_parsing"]["total_comments_seen"] == 2
    assert audit["raw_comments_persisted"]["total_comments_seen"] == 2
    assert audit["normalized_comments"]["total_comments_seen"] == 2
    assert audit["classification_inputs"]["total_comments_seen"] == 2
    assert audit["classified_comments"]["total_comments_seen"] == 2
    assert audit["classified_comments"]["earliest_comment_date"].startswith("2025-07-08")
    assert audit["classified_comments"]["latest_comment_date"].startswith("2026-03-07")
    assert audit["classified_comments"]["months_represented"] == 2
