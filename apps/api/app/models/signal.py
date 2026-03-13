from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampedModel
from app.models.enums import MvpArea, PrimaryCategory, SignalStatus


class MvpSignal(TimestampedModel, Base):
    """Grouped product signal derived from one or more classified comments."""

    __tablename__ = "mvp_signals"

    fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    mvp_area: Mapped[MvpArea] = mapped_column(Enum(MvpArea), nullable=False)
    primary_category: Mapped[PrimaryCategory] = mapped_column(Enum(PrimaryCategory), nullable=False)
    status: Mapped[SignalStatus] = mapped_column(Enum(SignalStatus), nullable=False, default=SignalStatus.ACTIVE)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sample_comments: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    suggested_backlog_action: Mapped[str] = mapped_column(String(255), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[str | None] = mapped_column(String(255))
    export_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    comment_links: Mapped[list["SignalCommentLink"]] = relationship(back_populates="signal")


class SignalCommentLink(TimestampedModel, Base):
    """Associates classified comments with the signal they support."""

    __tablename__ = "signal_comment_links"
    __table_args__ = (UniqueConstraint("signal_id", "normalized_comment_id", name="uq_signal_comment_link"),)

    signal_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("mvp_signals.id"), nullable=False)
    normalized_comment_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("normalized_comments.id"), nullable=False)
    classification_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("comment_classifications.id"))
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    signal: Mapped["MvpSignal"] = relationship(back_populates="comment_links")
    normalized_comment: Mapped["NormalizedComment"] = relationship(back_populates="signal_links")
    classification: Mapped["CommentClassification | None"] = relationship(back_populates="signal_links")
