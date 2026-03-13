from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ClassificationStatus, NormalizationStatus, SourcePlatform
from app.schemas.classifications import CommentClassificationRead
from app.schemas.common import ORMModel


class CommentFilters(BaseModel):
    keyword: str | None = None
    source_video_id: str | None = None
    primary_category: str | None = None
    mvp_area: str | None = None
    sentiment: str | None = None
    needs_human_review: bool | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 50
    offset: int = 0


class RawCommentRead(ORMModel):
    id: UUID
    ingestion_run_id: UUID
    source_platform: SourcePlatform
    source_video_id: str
    source_comment_id: str
    author_handle: str | None
    comment_text: str
    comment_created_at: datetime | None
    like_count: int
    reply_count: int
    row_number: int | None
    is_duplicate: bool
    created_at: datetime
    updated_at: datetime


class NormalizedCommentRead(ORMModel):
    id: UUID
    raw_comment_id: UUID
    ingestion_run_id: UUID
    source_platform: SourcePlatform
    source_video_id: str
    source_comment_id: str
    author_handle: str | None
    original_text: str
    normalized_text: str
    comment_created_at: datetime | None
    like_count: int
    reply_count: int
    normalization_status: NormalizationStatus
    classification_status: ClassificationStatus
    rules_matched: list[str]
    created_at: datetime
    updated_at: datetime


class CommentListItem(ORMModel):
    raw_comment: RawCommentRead
    normalized_comment: NormalizedCommentRead | None = None
    classification: CommentClassificationRead | None = None


class CommentDetail(CommentListItem):
    pass
