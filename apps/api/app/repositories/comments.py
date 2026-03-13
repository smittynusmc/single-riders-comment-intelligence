from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment, RawComment
from app.models.enums import ClassificationStatus, NormalizationStatus, SourcePlatform


class CommentRepository:
    def __init__(self, session: Session):
        self.session = session

    def existing_source_comment_ids(self, *, source_platform: SourcePlatform, source_comment_ids: list[str]) -> set[str]:
        if not source_comment_ids:
            return set()
        stmt = select(NormalizedComment.source_comment_id).where(
            NormalizedComment.source_platform == source_platform,
            NormalizedComment.source_comment_id.in_(source_comment_ids),
        )
        return set(self.session.scalars(stmt))

    def create_raw_comments(self, raw_comments: list[RawComment]) -> list[RawComment]:
        self.session.add_all(raw_comments)
        self.session.flush()
        return raw_comments

    def create_normalized_comment(self, normalized_comment: NormalizedComment) -> NormalizedComment:
        self.session.add(normalized_comment)
        self.session.flush()
        return normalized_comment

    def pending_raw_comments_for_run(self, run_id: UUID) -> list[RawComment]:
        stmt = (
            select(RawComment)
            .where(RawComment.ingestion_run_id == run_id, RawComment.is_duplicate.is_(False))
            .order_by(RawComment.created_at.asc())
        )
        return list(self.session.scalars(stmt))

    def normalized_comments_for_run(self, run_id: UUID, *, pending_only: bool = False) -> list[NormalizedComment]:
        stmt = select(NormalizedComment).where(NormalizedComment.ingestion_run_id == run_id)
        if pending_only:
            stmt = stmt.where(NormalizedComment.classification_status == ClassificationStatus.PENDING)
        stmt = stmt.order_by(NormalizedComment.created_at.asc())
        return list(self.session.scalars(stmt))

    def get_normalized_by_source(self, *, source_platform: SourcePlatform, source_comment_id: str) -> NormalizedComment | None:
        stmt = select(NormalizedComment).where(
            NormalizedComment.source_platform == source_platform,
            NormalizedComment.source_comment_id == source_comment_id,
        )
        return self.session.scalar(stmt)

    def list_comments(
        self,
        *,
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
    ) -> tuple[list[tuple[RawComment, NormalizedComment | None, CommentClassification | None]], int]:
        stmt = (
            select(RawComment, NormalizedComment, CommentClassification)
            .outerjoin(NormalizedComment, RawComment.id == NormalizedComment.raw_comment_id)
            .outerjoin(CommentClassification, CommentClassification.normalized_comment_id == NormalizedComment.id)
        )

        if keyword:
            pattern = f"%{keyword.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(RawComment.comment_text).like(pattern),
                    func.lower(NormalizedComment.normalized_text).like(pattern),
                )
            )
        if source_video_id:
            stmt = stmt.where(RawComment.source_video_id == source_video_id)
        if primary_category:
            stmt = stmt.where(CommentClassification.primary_category == primary_category)
        if mvp_area:
            stmt = stmt.where(CommentClassification.mvp_area == mvp_area)
        if sentiment:
            stmt = stmt.where(CommentClassification.sentiment == sentiment)
        if needs_human_review is not None:
            stmt = stmt.where(CommentClassification.needs_human_review == needs_human_review)
        if date_from:
            stmt = stmt.where(RawComment.comment_created_at >= date_from)
        if date_to:
            stmt = stmt.where(RawComment.comment_created_at <= date_to)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.scalar(count_stmt) or 0

        stmt = stmt.order_by(RawComment.comment_created_at.desc().nullslast(), RawComment.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).all()), total

    def get_comment_detail(self, comment_id: UUID) -> tuple[RawComment, NormalizedComment | None, CommentClassification | None] | None:
        stmt = (
            select(RawComment, NormalizedComment, CommentClassification)
            .outerjoin(NormalizedComment, RawComment.id == NormalizedComment.raw_comment_id)
            .outerjoin(CommentClassification, CommentClassification.normalized_comment_id == NormalizedComment.id)
            .where(RawComment.id == comment_id)
        )
        return self.session.execute(stmt).one_or_none()

    def update_classification_status(self, normalized_comment: NormalizedComment, status: ClassificationStatus) -> None:
        normalized_comment.classification_status = status
        self.session.add(normalized_comment)
        self.session.flush()

    def update_normalization_status(self, normalized_comment: NormalizedComment, status: NormalizationStatus) -> None:
        normalized_comment.normalization_status = status
        self.session.add(normalized_comment)
        self.session.flush()
