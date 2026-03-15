from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampedModel, value_enum
from app.models.enums import ImportFormat, IngestionSourceType, IngestionStatus, SourcePlatform


class IngestionRun(TimestampedModel, Base):
    """Tracks a single import execution from any adapter."""

    __tablename__ = "ingestion_runs"

    source_type: Mapped[IngestionSourceType] = mapped_column(
        value_enum(IngestionSourceType, name="ingestionsourcetype"),
        nullable=False,
    )
    source_platform: Mapped[SourcePlatform] = mapped_column(
        value_enum(SourcePlatform, name="sourceplatform"),
        nullable=False,
    )
    import_format: Mapped[ImportFormat] = mapped_column(
        value_enum(ImportFormat, name="importformat"),
        nullable=False,
    )
    source_label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[IngestionStatus] = mapped_column(
        value_enum(IngestionStatus, name="ingestionstatus"),
        nullable=False,
        default=IngestionStatus.PENDING,
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    uploaded_by_email: Mapped[str | None] = mapped_column(String(255))
    source_file_content_type: Mapped[str | None] = mapped_column(String(255))
    source_file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    source_file_sha256: Mapped[str | None] = mapped_column(String(64))
    source_file_blob: Mapped[bytes | None] = mapped_column(LargeBinary)
    run_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    raw_comments: Mapped[list["RawComment"]] = relationship(back_populates="ingestion_run")
    normalized_comments: Mapped[list["NormalizedComment"]] = relationship(back_populates="ingestion_run")
