from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, BinaryIO

from app.adapters.base import AdapterImportFailure, AdapterImportResult, BaseIngestionAdapter, CanonicalCommentObject
from app.models.enums import ImportFormat, IngestionSourceType, SourcePlatform


class TikTokResearchAdapter(BaseIngestionAdapter):
    """Parses approved TikTok Research API response JSON when it is supplied manually.

    This adapter only handles uploaded JSON payloads. It does not perform live API calls or assume
    comment access is available through standard TikTok OAuth.
    """

    source_type = IngestionSourceType.RESEARCH_API
    source_platform = SourcePlatform.TIKTOK

    def fetch_comments(self, file_content: bytes | str | BinaryIO) -> list[dict[str, Any]]:
        payload = self._load_json(file_content)
        records = self._extract_records(payload)
        if not records:
            raise ValueError("JSON payload is not a supported TikTok Research API comment response.")
        return records

    def import_comments(self, file_content: bytes | str | BinaryIO) -> AdapterImportResult:
        rows = self.fetch_comments(file_content)
        comments: list[CanonicalCommentObject] = []
        failures: list[AdapterImportFailure] = []

        for index, row in enumerate(rows, start=1):
            try:
                comments.append(self.normalize_payload(row, row_number=index))
            except Exception as exc:
                failures.append(
                    AdapterImportFailure(
                        row_number=index,
                        error=str(exc),
                        raw_payload=dict(row),
                    )
                )

        return AdapterImportResult(
            source_type=self.source_type,
            source_platform=self.source_platform,
            import_format=ImportFormat.RESEARCH_API_JSON,
            detected_shape="research_api.data",
            comments=comments,
            failures=failures,
        )

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> CanonicalCommentObject:
        source_comment_id = self._as_string(payload.get("id") or payload.get("comment_id"))
        comment_text = self._as_string(payload.get("text") or payload.get("comment_text"))
        if not source_comment_id or not comment_text:
            raise ValueError("Research API comment items must include id and text fields.")

        return CanonicalCommentObject(
            platform=self.source_platform,
            source_type="research_api_json",
            source_video_id=self._as_string(payload.get("video_id")),
            source_comment_id=source_comment_id,
            source_parent_comment_id=self._as_string(payload.get("parent_comment_id")),
            author_handle=self._author_handle(payload),
            comment_text=comment_text,
            comment_created_at=self._parse_datetime(payload.get("create_time")),
            like_count=int(payload.get("like_count") or 0),
            reply_count=int(payload.get("reply_count") or 0),
            raw_payload=dict(payload),
            row_number=row_number,
        )

    def _load_json(self, file_content: bytes | str | BinaryIO) -> Any:
        if hasattr(file_content, "read"):
            raw = file_content.read()
            content = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
        elif isinstance(file_content, bytes):
            content = file_content.decode("utf-8-sig")
        else:
            content = file_content
        return json.loads(content)

    def _extract_records(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            records = [item for item in payload["data"] if isinstance(item, dict)]
        elif isinstance(payload, list):
            records = [item for item in payload if isinstance(item, dict)]
        else:
            return []

        if not records:
            return []

        if not any(self._looks_like_research_comment(item) for item in records):
            return []

        return records

    def _looks_like_research_comment(self, payload: dict[str, Any]) -> bool:
        return bool(payload.get("id") and payload.get("text"))

    def _author_handle(self, payload: dict[str, Any]) -> str | None:
        user = payload.get("user")
        if isinstance(user, dict):
            return self._as_string(user.get("username") or user.get("unique_id"))
        return self._as_string(payload.get("username") or payload.get("author_handle"))

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=UTC)
        if isinstance(value, str) and value.isdigit():
            numeric = float(value)
            if len(value) > 10:
                numeric = numeric / 1000
            return datetime.fromtimestamp(numeric, tz=UTC)
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None

    def _as_string(self, value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value).strip() or None
