from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import ImportFormat, IngestionSourceType, IngestionStatus, SourcePlatform
from app.models.ingestion import IngestionRun


class IngestionRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        source_type: IngestionSourceType,
        source_platform: SourcePlatform,
        import_format: ImportFormat,
        source_label: str,
        uploaded_by_email: str | None = None,
        source_file_content_type: str | None = None,
        source_file_size_bytes: int | None = None,
        source_file_sha256: str | None = None,
        source_file_blob: bytes | None = None,
        run_metadata: dict | None = None,
        status: IngestionStatus = IngestionStatus.PENDING,
    ) -> IngestionRun:
        run = IngestionRun(
            source_type=source_type,
            source_platform=source_platform,
            import_format=import_format,
            source_label=source_label,
            uploaded_by_email=uploaded_by_email,
            source_file_content_type=source_file_content_type,
            source_file_size_bytes=source_file_size_bytes,
            source_file_sha256=source_file_sha256,
            source_file_blob=source_file_blob,
            status=status,
            started_at=datetime.now(UTC),
            run_metadata=run_metadata or {},
        )
        self.session.add(run)
        self.session.flush()
        return run

    def get(self, run_id: UUID) -> IngestionRun | None:
        return self.session.get(IngestionRun, run_id)

    def list(self, *, limit: int = 50, offset: int = 0) -> tuple[list[IngestionRun], int]:
        total = self.session.scalar(select(func.count()).select_from(IngestionRun)) or 0
        stmt = select(IngestionRun).order_by(IngestionRun.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt)), total

    def apply_summary(
        self,
        run: IngestionRun,
        *,
        total_rows: int,
        imported_rows: int,
        duplicate_rows: int,
        failed_rows: int,
        status: IngestionStatus,
        error_message: str | None = None,
    ) -> IngestionRun:
        run.total_rows = total_rows
        run.imported_rows = imported_rows
        run.duplicate_rows = duplicate_rows
        run.failed_rows = failed_rows
        run.status = status
        run.error_message = error_message
        if status in {IngestionStatus.COMPLETED, IngestionStatus.FAILED}:
            run.finished_at = datetime.now(UTC)
        self.session.add(run)
        self.session.flush()
        return run
