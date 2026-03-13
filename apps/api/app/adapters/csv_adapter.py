from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, BinaryIO

from app.adapters.base import AdapterImportFailure, AdapterImportResult, BaseIngestionAdapter, ImportedCommentRecord
from app.models.enums import IngestionSourceType, SourcePlatform

REQUIRED_COLUMNS = {
    "source_video_id",
    "source_comment_id",
    "author_handle",
    "comment_text",
    "created_at",
    "like_count",
    "reply_count",
}


class CsvImportAdapter(BaseIngestionAdapter):
    """CSV adapter that fully exercises the platform without live TikTok access."""

    source_type = IngestionSourceType.CSV
    source_platform = SourcePlatform.TIKTOK

    def fetch_comments(self, file_content: bytes | str | BinaryIO) -> list[dict[str, Any]]:
        if hasattr(file_content, "read"):
            raw = file_content.read()
            content = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        elif isinstance(file_content, bytes):
            content = file_content.decode("utf-8")
        else:
            content = file_content

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row.")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(sorted(missing))}")

        return [row for row in reader]

    def import_comments(self, file_content: bytes | str | BinaryIO) -> AdapterImportResult:
        rows = self.fetch_comments(file_content)
        comments: list[ImportedCommentRecord] = []
        failures: list[AdapterImportFailure] = []

        for index, row in enumerate(rows, start=2):
            try:
                comments.append(self.normalize_payload(row, row_number=index))
            except Exception as exc:  # pragma: no cover - defensive for arbitrary CSV content
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
            comments=comments,
            failures=failures,
        )

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> ImportedCommentRecord:
        comment_text = (payload.get("comment_text") or "").strip()
        if not comment_text:
            raise ValueError("comment_text is required")

        source_comment_id = str(payload.get("source_comment_id") or "").strip()
        source_video_id = str(payload.get("source_video_id") or "").strip()
        if not source_comment_id or not source_video_id:
            raise ValueError("source_comment_id and source_video_id are required")

        created_at_value = (payload.get("created_at") or "").strip()
        created_at = None
        if created_at_value:
            created_at = datetime.fromisoformat(created_at_value.replace("Z", "+00:00"))

        return ImportedCommentRecord(
            source_platform=self.source_platform,
            source_video_id=source_video_id,
            source_comment_id=source_comment_id,
            author_handle=(payload.get("author_handle") or "").strip() or None,
            comment_text=comment_text,
            created_at=created_at,
            like_count=int(payload.get("like_count") or 0),
            reply_count=int(payload.get("reply_count") or 0),
            row_number=row_number,
            payload=dict(payload),
        )
