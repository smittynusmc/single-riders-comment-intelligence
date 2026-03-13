from __future__ import annotations

from typing import Any

from app.adapters.base import AdapterImportResult, BaseIngestionAdapter, ImportedCommentRecord
from app.models.enums import IngestionSourceType, SourcePlatform


class TikTokConnectorPlaceholderAdapter(BaseIngestionAdapter):
    """Placeholder for future approved TikTok connectors.

    This intentionally does not assume undocumented TikTok APIs.
    """

    source_type = IngestionSourceType.CONNECTOR_PLACEHOLDER
    source_platform = SourcePlatform.TIKTOK

    def fetch_comments(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise NotImplementedError("Live TikTok connectors are not implemented in phase 1.")

    def import_comments(self, *args: Any, **kwargs: Any) -> AdapterImportResult:
        raise NotImplementedError("Live TikTok connectors are not implemented in phase 1.")

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> ImportedCommentRecord:
        raise NotImplementedError("Live TikTok connectors are not implemented in phase 1.")
