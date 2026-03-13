from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.repositories.comments import CommentRepository
from app.schemas.comments import CommentDetail, CommentListItem
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/comments")


def _serialize_comment_item(row: tuple) -> CommentListItem:
    raw_comment, normalized_comment, classification = row
    return CommentListItem.model_validate(
        {
            "raw_comment": raw_comment,
            "normalized_comment": normalized_comment,
            "classification": classification,
        }
    )


@router.get("", response_model=PaginatedResponse[CommentListItem])
def list_comments(
    keyword: str | None = None,
    source_video_id: str | None = None,
    primary_category: str | None = None,
    mvp_area: str | None = None,
    sentiment: str | None = None,
    needs_human_review: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(db_session),
) -> PaginatedResponse[CommentListItem]:
    rows, total = CommentRepository(session).list_comments(
        keyword=keyword,
        source_video_id=source_video_id,
        primary_category=primary_category,
        mvp_area=mvp_area,
        sentiment=sentiment,
        needs_human_review=needs_human_review,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse[CommentListItem](
        items=[_serialize_comment_item(row) for row in rows],
        meta=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{comment_id}", response_model=CommentDetail)
def get_comment(comment_id: UUID, session: Session = Depends(db_session)) -> CommentDetail:
    row = CommentRepository(session).get_comment_detail(comment_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    return CommentDetail.model_validate(_serialize_comment_item(row).model_dump())
