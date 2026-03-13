from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ClassificationStatus, MvpArea, PrimaryCategory, SentimentLabel
from app.schemas.common import ORMModel


class ClassificationResultPayload(BaseModel):
    primary_category: PrimaryCategory
    secondary_categories: list[str] = Field(default_factory=list)
    mvp_area: MvpArea
    sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    mvp_relevance_score: float = Field(ge=0.0, le=1.0)
    urgency_score: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool
    recommended_action: str
    rationale_short: str


class CommentClassificationRead(ORMModel):
    id: UUID
    normalized_comment_id: UUID
    provider: str
    model_name: str
    prompt_version: str
    primary_category: PrimaryCategory
    secondary_categories: list[str]
    mvp_area: MvpArea
    sentiment: SentimentLabel
    confidence: float
    mvp_relevance_score: float
    urgency_score: float
    needs_human_review: bool
    recommended_action: str
    rationale_short: str
    review_status: ClassificationStatus
    reviewer_note: str | None
    reviewed_at: datetime | None
    override_primary_category: PrimaryCategory | None
    override_mvp_area: MvpArea | None
    is_false_positive: bool
    created_at: datetime
    updated_at: datetime


class NormalizedCommentReviewContext(ORMModel):
    id: UUID
    source_video_id: str
    source_comment_id: str
    author_handle: str | None
    original_text: str
    normalized_text: str
    comment_created_at: datetime | None
    like_count: int
    reply_count: int
    rules_matched: list[str]


class ClassificationReviewItem(ORMModel):
    classification: CommentClassificationRead
    normalized_comment: NormalizedCommentReviewContext


class ClassificationUpdate(BaseModel):
    review_status: ClassificationStatus | None = None
    reviewer_note: str | None = None
    override_primary_category: PrimaryCategory | None = None
    override_mvp_area: MvpArea | None = None
    is_false_positive: bool | None = None
