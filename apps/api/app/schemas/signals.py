from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import MvpArea, PrimaryCategory, SignalStatus
from app.schemas.common import ORMModel


class SignalCommentEvidence(BaseModel):
    normalized_comment_id: UUID
    classification_id: UUID | None = None
    comment_text: str
    author_handle: str | None = None
    relevance_score: float


class SignalRead(ORMModel):
    id: UUID
    fingerprint: str
    title: str
    summary: str
    mvp_area: MvpArea
    primary_category: PrimaryCategory
    status: SignalStatus
    evidence_count: int
    priority_score: float
    first_seen_at: datetime | None
    last_seen_at: datetime | None
    sample_comments: list[dict]
    suggested_backlog_action: str
    reviewed_at: datetime | None
    reviewed_by: str | None
    export_metadata: dict
    created_at: datetime
    updated_at: datetime


class SignalDetail(SignalRead):
    linked_comments: list[SignalCommentEvidence]


class SignalUpdate(BaseModel):
    status: SignalStatus | None = None
    reviewed_by: str | None = None


class SignalExportResponse(BaseModel):
    signal_id: UUID
    destination: str
    status: str
    reference: str | None = None
