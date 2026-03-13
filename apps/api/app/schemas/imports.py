from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ImportFormat, IngestionSourceType, IngestionStatus, SourcePlatform
from app.schemas.common import ORMModel


class ImportResponse(BaseModel):
    ingestion_run_id: UUID
    status: IngestionStatus
    imported_rows: int
    duplicate_rows: int
    failed_rows: int


class ImportPreviewSample(BaseModel):
    source_comment_id: str
    source_video_id: str | None = None
    author_handle: str | None = None
    comment_text: str
    comment_created_at: datetime | None = None


class ImportPreviewResponse(BaseModel):
    detected_format: ImportFormat
    detected_shape: str | None = None
    comment_count: int
    sample_fields: list[str]
    missing_fields: list[str]
    parse_warnings: list[str]
    sample_comments: list[ImportPreviewSample]


class IngestionRunRead(ORMModel):
    id: UUID
    source_type: IngestionSourceType
    source_platform: SourcePlatform
    import_format: ImportFormat
    source_label: str
    status: IngestionStatus
    total_rows: int
    imported_rows: int
    duplicate_rows: int
    failed_rows: int
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    run_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
