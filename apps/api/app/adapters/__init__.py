from __future__ import annotations

from app.adapters.base import AdapterImportFailure, AdapterImportResult, BaseIngestionAdapter, ImportedCommentRecord
from app.adapters.csv_adapter import CsvImportAdapter
from app.adapters.json_adapter import JsonImportAdapter, TikTokJsonImportAdapter
from app.adapters.manual_paste import ManualPasteAdapter
from app.adapters.third_party_export import ThirdPartyExportPlaceholderAdapter
from app.adapters.tiktok_placeholder import TikTokConnectorPlaceholderAdapter
from app.adapters.tiktok_research import TikTokResearchAdapter

__all__ = [
    "AdapterImportFailure",
    "AdapterImportResult",
    "BaseIngestionAdapter",
    "CsvImportAdapter",
    "ImportedCommentRecord",
    "JsonImportAdapter",
    "TikTokJsonImportAdapter",
    "ManualPasteAdapter",
    "ThirdPartyExportPlaceholderAdapter",
    "TikTokConnectorPlaceholderAdapter",
    "TikTokResearchAdapter",
]
