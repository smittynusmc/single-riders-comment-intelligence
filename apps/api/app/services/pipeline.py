from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment, RawComment
from app.models.enums import IngestionStatus
from app.repositories.ingestion_runs import IngestionRunRepository
from app.repositories.signals import SignalRepository
from app.services.aggregation import SignalAggregationService
from app.services.classification import CommentClassificationService
from app.services.normalization import NormalizationService

logger = logging.getLogger(__name__)


class IngestionPipelineService:
    """Coordinates normalization, classification, and signal rebuilds for an import run."""

    def __init__(
        self,
        *,
        ingestion_repository: IngestionRunRepository,
        normalization_service: NormalizationService,
        classification_service: CommentClassificationService,
        aggregation_service: SignalAggregationService,
        signal_repository: SignalRepository,
    ):
        self.ingestion_repository = ingestion_repository
        self.normalization_service = normalization_service
        self.classification_service = classification_service
        self.aggregation_service = aggregation_service
        self.signal_repository = signal_repository

    def process_run(self, run_id: UUID):
        run = self.ingestion_repository.get(run_id)
        if not run:
            raise ValueError(f"Ingestion run {run_id} was not found.")

        run.status = IngestionStatus.PROCESSING
        run.started_at = run.started_at or datetime.now(UTC)
        self.ingestion_repository.session.add(run)
        self.ingestion_repository.session.flush()

        normalized_comments = self.normalization_service.normalize_run(run_id)
        if not normalized_comments:
            normalized_comments = self.normalization_service.comment_repository.normalized_comments_for_run(run_id, pending_only=True)
        classified_comments = self.classification_service.classify_comments(normalized_comments)
        signals, links = self.aggregation_service.rebuild(existing_signals=self.signal_repository.existing_by_fingerprint())
        self.signal_repository.replace_all(signals=signals, links=links)

        pipeline_audit = {
            **dict(run.run_metadata.get("pipeline_audit", {})),
            "normalized_comments": self._coverage_payload_for_model(run_id, NormalizedComment, NormalizedComment.comment_created_at),
            "classification_inputs": self._coverage_payload_from_normalized(normalized_comments),
            "classified_comments": self._coverage_payload_for_classifications(run_id),
        }
        run.run_metadata = {
            **dict(run.run_metadata),
            "pipeline_audit": pipeline_audit,
        }
        logger.info(
            "Pipeline processed run %s with normalized=%s classified=%s signals=%s",
            run_id,
            pipeline_audit["normalized_comments"]["total_comments_seen"],
            pipeline_audit["classified_comments"]["total_comments_seen"],
            len(signals),
        )

        run.status = IngestionStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.ingestion_repository.session.add(run)
        self.ingestion_repository.session.flush()
        return run

    def _coverage_payload_for_model(self, run_id: UUID, model, date_column) -> dict[str, str | int | None]:
        session = self.ingestion_repository.session
        total_comments_seen = session.scalar(select(func.count()).select_from(model).where(model.ingestion_run_id == run_id)) or 0
        rows = list(session.execute(select(date_column).where(model.ingestion_run_id == run_id)))
        dates = [row[0] if row[0] else None for row in rows]
        clean_dates = [value if value.tzinfo else value.replace(tzinfo=UTC) for value in dates if value is not None]
        return self._coverage_payload_from_dates(total_comments_seen=total_comments_seen, dates=clean_dates)

    def _coverage_payload_for_classifications(self, run_id: UUID) -> dict[str, str | int | None]:
        session = self.ingestion_repository.session
        rows = list(
            session.execute(
                select(NormalizedComment.comment_created_at, NormalizedComment.created_at)
                .join(CommentClassification, CommentClassification.normalized_comment_id == NormalizedComment.id)
                .where(NormalizedComment.ingestion_run_id == run_id)
            )
        )
        dates = [
            (comment_created_at or created_at).replace(tzinfo=UTC) if (comment_created_at or created_at) and not (comment_created_at or created_at).tzinfo else (comment_created_at or created_at)
            for comment_created_at, created_at in rows
            if comment_created_at is not None or created_at is not None
        ]
        return self._coverage_payload_from_dates(total_comments_seen=len(rows), dates=dates)

    def _coverage_payload_from_normalized(self, comments: list[NormalizedComment]) -> dict[str, str | int | None]:
        dates = [
            comment.comment_created_at if comment.comment_created_at and comment.comment_created_at.tzinfo else (comment.comment_created_at.replace(tzinfo=UTC) if comment.comment_created_at else None)
            for comment in comments
        ]
        clean_dates = [value for value in dates if value is not None]
        return self._coverage_payload_from_dates(total_comments_seen=len(comments), dates=clean_dates)

    def _coverage_payload_from_dates(self, *, total_comments_seen: int, dates: list[datetime]) -> dict[str, str | int | None]:
        if not dates:
            return {
                "total_comments_seen": total_comments_seen,
                "earliest_comment_date": None,
                "latest_comment_date": None,
                "months_represented": 0,
            }

        earliest = min(dates)
        latest = max(dates)
        months_represented = len({(value.year, value.month) for value in dates})
        return {
            "total_comments_seen": total_comments_seen,
            "earliest_comment_date": earliest.isoformat(),
            "latest_comment_date": latest.isoformat(),
            "months_represented": months_represented,
        }
