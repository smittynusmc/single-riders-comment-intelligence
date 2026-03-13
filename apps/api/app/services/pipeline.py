from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.enums import IngestionStatus
from app.repositories.ingestion_runs import IngestionRunRepository
from app.repositories.signals import SignalRepository
from app.services.aggregation import SignalAggregationService
from app.services.classification import CommentClassificationService
from app.services.normalization import NormalizationService


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
        self.classification_service.classify_comments(normalized_comments)
        signals, links = self.aggregation_service.rebuild(existing_signals=self.signal_repository.existing_by_fingerprint())
        self.signal_repository.replace_all(signals=signals, links=links)

        run.status = IngestionStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.ingestion_repository.session.add(run)
        self.ingestion_repository.session.flush()
        return run
