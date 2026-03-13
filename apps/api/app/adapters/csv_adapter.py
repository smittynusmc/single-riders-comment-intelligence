from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, BinaryIO

from app.adapters.base import AdapterImportFailure, AdapterImportResult, BaseIngestionAdapter, CanonicalCommentObject
from app.models.enums import ImportFormat, IngestionSourceType, SourcePlatform

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
    """Secondary CSV convenience adapter for cleaned/manual datasets."""

    source_type = IngestionSourceType.CSV_UPLOAD
    source_platform = SourcePlatform.TIKTOK

    def fetch_comments(self, file_content: bytes | str | BinaryIO) -> list[dict[str, Any]]:
        if hasattr(file_content, "read"):
            raw = file_content.read()
            content = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
        elif isinstance(file_content, bytes):
            content = file_content.decode("utf-8-sig")
        else:
            content = file_content

        reader = csv.DictReader(io.StringIO(content))
        if reader.fieldnames:
            reader.fieldnames = [field.lstrip("\ufeff") if field else field for field in reader.fieldnames]
        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row.")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(sorted(missing))}")

        return [row for row in reader]

    def import_comments(self, file_content: bytes | str | BinaryIO) -> AdapterImportResult:
        rows = self.fetch_comments(file_content)
        comments: list[CanonicalCommentObject] = []
        failures: list[AdapterImportFailure] = []

        for index, row in enumerate(rows, start=2):
            try:
                comments.append(self.normalize_payload(row, row_number=index))
            except Exception as exc:  # pragma: no cover
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
            import_format=ImportFormat.CSV,
            detected_shape="csv",
            comments=comments,
            failures=failures,
        )

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> CanonicalCommentObject:
        comment_text = (payload.get("comment_text") or "").strip()
        if not comment_text:
            raise ValueError("comment_text is required")

        source_comment_id = str(payload.get("source_comment_id") or "").strip()
        source_video_id = str(payload.get("source_video_id") or "").strip() or None
        if not source_comment_id:
            raise ValueError("source_comment_id is required")

        created_at_value = (payload.get("created_at") or "").strip()
        created_at = None
        if created_at_value:
            created_at = datetime.fromisoformat(created_at_value.replace("Z", "+00:00"))

        return CanonicalCommentObject(
            platform=self.source_platform,
            source_type="csv_upload",
            source_video_id=source_video_id,
            source_comment_id=source_comment_id,
            source_parent_comment_id=(payload.get("source_parent_comment_id") or "").strip() or None,
            author_handle=(payload.get("author_handle") or "").strip() or None,
            comment_text=comment_text,
            comment_created_at=created_at,
            like_count=int(payload.get("like_count") or 0),
            reply_count=int(payload.get("reply_count") or 0),
            raw_payload=dict(payload),
            row_number=row_number,
        )