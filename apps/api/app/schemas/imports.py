from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import IngestionSourceType, IngestionStatus, SourcePlatform
from app.schemas.common import ORMModel


class CsvImportResponse(BaseModel):
    ingestion_run_id: UUID
    status: IngestionStatus
    imported_rows: int
    duplicate_rows: int
    failed_rows: int


class IngestionRunRead(ORMModel):
    id: UUID
    source_type: IngestionSourceType
    source_platform: SourcePlatform
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
