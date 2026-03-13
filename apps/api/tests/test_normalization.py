from __future__ import annotations

from uuid import UUID

from app.models.comment import RawComment
from app.models.enums import SourcePlatform
from app.repositories.comments import CommentRepository
from app.services.normalization import NormalizationService
from app.services.rules import KeywordRuleService


def test_normalization_collapses_whitespace_and_applies_rules(db_session):
    repository = CommentRepository(db_session)
    service = NormalizationService(repository, KeywordRuleService())
    raw_comment = RawComment(
        ingestion_run_id=UUID("00000000-0000-0000-0000-000000000001"),
        source_platform=SourcePlatform.TIKTOK,
        source_video_id="video-1",
        source_comment_id="comment-1",
        author_handle="tester",
        comment_text="Need   a SAME DAY   meetup   option",
        like_count=0,
        reply_count=0,
        payload={},
    )

    payload = service.build_payload(raw_comment)

    assert payload.normalized_text == "need a same day meetup option"
    assert "meetup" in payload.rules_matched
