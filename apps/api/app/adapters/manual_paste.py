from __future__ import annotations

from datetime import datetime

from app.adapters.base import AdapterImportResult, BaseIngestionAdapter, ImportedCommentRecord
from app.models.enums import IngestionSourceType, SourcePlatform


class ManualPasteAdapter(BaseIngestionAdapter):
    """Placeholder adapter for pasted comments from internal review workflows."""

    source_type = IngestionSourceType.MANUAL_PASTE
    source_platform = SourcePlatform.MANUAL

    def fetch_comments(self, text_blob: str) -> list[dict[str, str]]:
        rows = []
        for index, line in enumerate(text_blob.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            rows.append({"source_comment_id": f"manual-{index}", "comment_text": line})
        return rows

    def import_comments(self, text_blob: str) -> AdapterImportResult:
        comments = [self.normalize_payload(row, row_number=index) for index, row in enumerate(self.fetch_comments(text_blob), start=1)]
        return AdapterImportResult(source_type=self.source_type, source_platform=self.source_platform, comments=comments)

    def normalize_payload(self, payload: dict[str, str], row_number: int | None = None) -> ImportedCommentRecord:
        return ImportedCommentRecord(
            source_platform=self.source_platform,
            source_video_id="manual-paste",
            source_comment_id=payload["source_comment_id"],
            comment_text=payload["comment_text"],
            row_number=row_number,
            payload=dict(payload),
        )
