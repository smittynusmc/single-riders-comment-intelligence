from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampedModel, value_enum
from app.models.enums import ClassificationStatus, MvpArea, PrimaryCategory, SentimentLabel


class CommentClassification(TimestampedModel, Base):
    """AI and rules-based classification output for a normalized comment."""

    __tablename__ = "comment_classifications"

    normalized_comment_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("normalized_comments.id"),
        nullable=False,
        unique=True,
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1")
    raw_response: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    primary_category: Mapped[PrimaryCategory] = mapped_column(
        value_enum(PrimaryCategory, name="primarycategory"),
        nullable=False,
    )
    secondary_categories: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mvp_area: Mapped[MvpArea] = mapped_column(value_enum(MvpArea, name="mvparea"), nullable=False)
    sentiment: Mapped[SentimentLabel] = mapped_column(
        value_enum(SentimentLabel, name="sentimentlabel"),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    mvp_relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    urgency_score: Mapped[float] = mapped_column(Float, nullable=False)
    needs_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recommended_action: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale_short: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[ClassificationStatus] = mapped_column(
        value_enum(ClassificationStatus, name="classificationstatus"),
        nullable=False,
        default=ClassificationStatus.CLASSIFIED,
    )
    reviewer_note: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    override_primary_category: Mapped[PrimaryCategory | None] = mapped_column(
        value_enum(PrimaryCategory, name="primarycategory"),
    )
    override_mvp_area: Mapped[MvpArea | None] = mapped_column(value_enum(MvpArea, name="mvparea"))
    is_false_positive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    normalized_comment: Mapped["NormalizedComment"] = relationship(back_populates="classification")
    signal_links: Mapped[list["SignalCommentLink"]] = relationship(back_populates="classification")
