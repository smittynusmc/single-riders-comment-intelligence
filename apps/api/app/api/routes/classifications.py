from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.enums import ClassificationStatus
from app.repositories.classifications import ClassificationRepository
from app.repositories.comments import CommentRepository
from app.schemas.classifications import (
    ClassificationReviewItem,
    ClassificationUpdate,
    CommentClassificationRead,
    NormalizedCommentReviewContext,
)
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/classifications")


@router.get("", response_model=PaginatedResponse[ClassificationReviewItem])
def list_classifications(
    needs_human_review: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(db_session),
) -> PaginatedResponse[ClassificationReviewItem]:
    repository = ClassificationRepository(session)
    items, total = repository.list(needs_human_review=needs_human_review, limit=limit, offset=offset)
    serialized = [
        ClassificationReviewItem(
            classification=CommentClassificationRead.model_validate(item),
            normalized_comment=NormalizedCommentReviewContext.model_validate(item.normalized_comment),
        )
        for item in items
    ]
    return PaginatedResponse[ClassificationReviewItem](
        items=serialized,
        meta=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.patch("/{classification_id}", response_model=CommentClassificationRead)
def update_classification(
    classification_id: UUID,
    payload: ClassificationUpdate,
    session: Session = Depends(db_session),
) -> CommentClassificationRead:
    classification_repository = ClassificationRepository(session)
    comment_repository = CommentRepository(session)
    classification = classification_repository.get(classification_id)
    if not classification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classification not found.")

    updated = classification_repository.apply_review_update(
        classification,
        payload.model_dump(exclude_none=True),
    )
    comment_repository.update_classification_status(updated.normalized_comment, updated.review_status)
    session.commit()
    session.refresh(updated)
    return CommentClassificationRead.model_validate(updated)
