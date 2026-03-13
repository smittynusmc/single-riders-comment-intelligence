from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampedModel
from app.models.enums import IngestionSourceType, IngestionStatus, SourcePlatform


class IngestionRun(TimestampedModel, Base):
    """Tracks a single import execution from any adapter."""

    __tablename__ = "ingestion_runs"

    source_type: Mapped[IngestionSourceType] = mapped_column(Enum(IngestionSourceType), nullable=False)
    source_platform: Mapped[SourcePlatform] = mapped_column(Enum(SourcePlatform), nullable=False)
    source_label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus),
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
    run_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    raw_comments: Mapped[list["RawComment"]] = relationship(back_populates="ingestion_run")
    normalized_comments: Mapped[list["NormalizedComment"]] = relationship(back_populates="ingestion_run")
