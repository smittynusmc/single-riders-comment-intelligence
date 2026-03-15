from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampedModel, value_enum
from app.models.enums import ClassificationStatus, NormalizationStatus, SourcePlatform


class RawComment(TimestampedModel, Base):
    """Stores the untouched canonical import object and raw payload for auditing and replay."""

    __tablename__ = "raw_comments"

    ingestion_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("ingestion_runs.id"), nullable=False)
    source_platform: Mapped[SourcePlatform] = mapped_column(
        value_enum(SourcePlatform, name="sourceplatform"),
        nullable=False,
    )
    source_video_id: Mapped[str | None] = mapped_column(String(255))
    source_comment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_parent_comment_id: Mapped[str | None] = mapped_column(String(255))
    author_handle: Mapped[str | None] = mapped_column(String(255))
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    comment_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    row_number: Mapped[int | None] = mapped_column(Integer)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    ingestion_run: Mapped["IngestionRun"] = relationship(back_populates="raw_comments")
    normalized_comment: Mapped["NormalizedComment | None"] = relationship(back_populates="raw_comment", uselist=False)


class NormalizedComment(TimestampedModel, Base):
    """Canonical comment shape used by rules, AI classification, and signal aggregation."""

    __tablename__ = "normalized_comments"
    __table_args__ = (UniqueConstraint("source_platform", "source_comment_id", name="uq_normalized_comment_source"),)

    raw_comment_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("raw_comments.id"), nullable=False, unique=True)
    ingestion_run_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("ingestion_runs.id"), nullable=False)
    source_platform: Mapped[SourcePlatform] = mapped_column(
        value_enum(SourcePlatform, name="sourceplatform"),
        nullable=False,
    )
    source_video_id: Mapped[str | None] = mapped_column(String(255))
    source_comment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_parent_comment_id: Mapped[str | None] = mapped_column(String(255))
    author_handle: Mapped[str | None] = mapped_column(String(255))
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    comment_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    normalization_status: Mapped[NormalizationStatus] = mapped_column(
        value_enum(NormalizationStatus, name="normalizationstatus"),
        nullable=False,
        default=NormalizationStatus.PENDING,
    )
    classification_status: Mapped[ClassificationStatus] = mapped_column(
        value_enum(ClassificationStatus, name="classificationstatus"),
        nullable=False,
        default=ClassificationStatus.PENDING,
    )
    rules_matched: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    raw_comment: Mapped["RawComment"] = relationship(back_populates="normalized_comment")
    ingestion_run: Mapped["IngestionRun"] = relationship(back_populates="normalized_comments")
    classification: Mapped["CommentClassification | None"] = relationship(
        back_populates="normalized_comment",
        uselist=False,
    )
    signal_links: Mapped[list["SignalCommentLink"]] = relationship(back_populates="normalized_comment")
