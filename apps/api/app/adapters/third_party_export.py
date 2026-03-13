from __future__ import annotations

from typing import Any

from app.adapters.base import AdapterImportResult, BaseIngestionAdapter, ImportedCommentRecord
from app.models.enums import ImportFormat, IngestionSourceType, SourcePlatform


class ThirdPartyExportPlaceholderAdapter(BaseIngestionAdapter):
    """Placeholder for future approved exports from social listening tools."""

    source_type = IngestionSourceType.THIRD_PARTY_EXPORT
    source_platform = SourcePlatform.GENERIC_SOCIAL
    import_format = ImportFormat.THIRD_PARTY_EXPORT

    def fetch_comments(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise NotImplementedError("Third-party export adapters are documented placeholders in phase 1.")

    def import_comments(self, *args: Any, **kwargs: Any) -> AdapterImportResult:
        raise NotImplementedError("Third-party export adapters are documented placeholders in phase 1.")

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> ImportedCommentRecord:
        raise NotImplementedError("Third-party export adapters are documented placeholders in phase 1.")
