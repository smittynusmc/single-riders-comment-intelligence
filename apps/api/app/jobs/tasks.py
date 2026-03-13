from __future__ import annotations

from uuid import UUID

from app.db.session import SessionLocal
from app.repositories.classifications import ClassificationRepository
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.repositories.signals import SignalRepository
from app.services.aggregation import SignalAggregationService
from app.services.classification import ClassificationResultParser, CommentClassificationService
from app.services.normalization import NormalizationService
from app.services.pipeline import IngestionPipelineService
from app.services.rules import KeywordRuleService


def process_ingestion_run(run_id: str) -> None:
    session = SessionLocal()
    try:
        rule_service = KeywordRuleService()
        comment_repository = CommentRepository(session)
        pipeline = IngestionPipelineService(
            ingestion_repository=IngestionRunRepository(session),
            normalization_service=NormalizationService(comment_repository, rule_service),
            classification_service=CommentClassificationService(
                comment_repository=comment_repository,
                classification_repository=ClassificationRepository(session),
                rule_service=rule_service,
                parser=ClassificationResultParser(),
            ),
            aggregation_service=SignalAggregationService(ClassificationRepository(session)),
            signal_repository=SignalRepository(session),
        )
        pipeline.process_run(UUID(run_id))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
