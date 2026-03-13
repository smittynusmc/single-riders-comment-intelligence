from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment
from app.models.enums import ClassificationStatus


class ClassificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, *, normalized_comment: NormalizedComment, values: dict) -> CommentClassification:
        existing = self.session.scalar(
            select(CommentClassification).where(CommentClassification.normalized_comment_id == normalized_comment.id)
        )
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            classification = existing
        else:
            classification = CommentClassification(normalized_comment_id=normalized_comment.id, **values)
            self.session.add(classification)

        self.session.flush()
        return classification

    def get(self, classification_id: UUID) -> CommentClassification | None:
        stmt = (
            select(CommentClassification)
            .options(selectinload(CommentClassification.normalized_comment))
            .where(CommentClassification.id == classification_id)
        )
        return self.session.scalar(stmt)

    def list(
        self,
        *,
        needs_human_review: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[CommentClassification], int]:
        stmt = select(CommentClassification).options(selectinload(CommentClassification.normalized_comment))
        if needs_human_review is not None:
            stmt = stmt.where(CommentClassification.needs_human_review == needs_human_review)

        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.order_by(CommentClassification.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt)), total

    def active_for_signal_build(self) -> list[CommentClassification]:
        stmt = (
            select(CommentClassification)
            .options(selectinload(CommentClassification.normalized_comment))
            .where(CommentClassification.is_false_positive.is_(False))
        )
        return list(self.session.scalars(stmt))

    def apply_review_update(self, classification: CommentClassification, values: dict) -> CommentClassification:
        for key, value in values.items():
            if value is not None:
                setattr(classification, key, value)

        if classification.is_false_positive:
            classification.review_status = ClassificationStatus.FALSE_POSITIVE
        elif classification.override_primary_category or classification.override_mvp_area:
            classification.review_status = ClassificationStatus.APPROVED
        elif classification.review_status == ClassificationStatus.APPROVED:
            classification.reviewed_at = datetime.utcnow()

        if classification.review_status in {ClassificationStatus.APPROVED, ClassificationStatus.FALSE_POSITIVE}:
            classification.reviewed_at = datetime.utcnow()

        self.session.add(classification)
        self.session.flush()
        return classification
