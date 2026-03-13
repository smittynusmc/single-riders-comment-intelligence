from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.comment import NormalizedComment, RawComment
from app.models.enums import ClassificationStatus, NormalizationStatus, SourcePlatform
from app.repositories.comments import CommentRepository
from app.services.rules import KeywordRuleService

WHITESPACE_RE = re.compile(r"\s+")


class NormalizedCommentData(BaseModel):
    raw_comment_id: UUID
    ingestion_run_id: UUID
    source_platform: SourcePlatform
    source_video_id: str
    source_comment_id: str
    author_handle: str | None = None
    original_text: str
    normalized_text: str
    comment_created_at: datetime | None = None
    like_count: int = 0
    reply_count: int = 0
    rules_matched: list[str] = Field(default_factory=list)


class NormalizationService:
    """Normalizes raw comments into canonical text for downstream processing."""

    def __init__(self, comment_repository: CommentRepository, rule_service: KeywordRuleService):
        self.comment_repository = comment_repository
        self.rule_service = rule_service

    def normalize_text(self, text: str) -> str:
        return WHITESPACE_RE.sub(" ", text).strip().lower()

    def build_payload(self, raw_comment: RawComment) -> NormalizedCommentData:
        normalized_text = self.normalize_text(raw_comment.comment_text)
        rules = self.rule_service.evaluate(normalized_text)
        return NormalizedCommentData(
            raw_comment_id=raw_comment.id,
            ingestion_run_id=raw_comment.ingestion_run_id,
            source_platform=raw_comment.source_platform,
            source_video_id=raw_comment.source_video_id,
            source_comment_id=raw_comment.source_comment_id,
            author_handle=raw_comment.author_handle,
            original_text=raw_comment.comment_text,
            normalized_text=normalized_text,
            comment_created_at=raw_comment.comment_created_at,
            like_count=raw_comment.like_count,
            reply_count=raw_comment.reply_count,
            rules_matched=rules.tags,
        )

    def normalize_run(self, run_id: UUID) -> list[NormalizedComment]:
        normalized_comments: list[NormalizedComment] = []
        for raw_comment in self.comment_repository.pending_raw_comments_for_run(run_id):
            existing = self.comment_repository.get_normalized_by_source(
                source_platform=raw_comment.source_platform,
                source_comment_id=raw_comment.source_comment_id,
            )
            if existing:
                raw_comment.is_duplicate = True
                self.comment_repository.session.add(raw_comment)
                continue

            payload = self.build_payload(raw_comment)
            normalized_comment = NormalizedComment(
                raw_comment_id=payload.raw_comment_id,
                ingestion_run_id=payload.ingestion_run_id,
                source_platform=payload.source_platform,
                source_video_id=payload.source_video_id,
                source_comment_id=payload.source_comment_id,
                author_handle=payload.author_handle,
                original_text=payload.original_text,
                normalized_text=payload.normalized_text,
                comment_created_at=payload.comment_created_at,
                like_count=payload.like_count,
                reply_count=payload.reply_count,
                normalization_status=NormalizationStatus.NORMALIZED,
                classification_status=ClassificationStatus.PENDING,
                rules_matched=payload.rules_matched,
            )
            normalized_comments.append(self.comment_repository.create_normalized_comment(normalized_comment))

        return normalized_comments
