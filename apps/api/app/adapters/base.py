from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Any, BinaryIO

from pydantic import BaseModel, Field

from app.models.enums import IngestionSourceType, SourcePlatform


class ImportedCommentRecord(BaseModel):
    source_platform: SourcePlatform = SourcePlatform.TIKTOK
    source_video_id: str
    source_comment_id: str
    author_handle: str | None = None
    comment_text: str
    created_at: datetime | None = None
    like_count: int = 0
    reply_count: int = 0
    row_number: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class AdapterImportFailure(BaseModel):
    row_number: int | None = None
    error: str
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class AdapterImportResult(BaseModel):
    source_type: IngestionSourceType
    source_platform: SourcePlatform
    comments: list[ImportedCommentRecord] = Field(default_factory=list)
    failures: list[AdapterImportFailure] = Field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return len(self.comments) + len(self.failures)


class BaseIngestionAdapter(ABC):
    """Interface for comment ingestion adapters."""

    source_type: IngestionSourceType
    source_platform: SourcePlatform

    @abstractmethod
    def fetch_comments(self, *args: Any, **kwargs: Any) -> Iterable[dict[str, Any]]:
        """Fetch comment payloads from the adapter source."""

    @abstractmethod
    def import_comments(self, *args: Any, **kwargs: Any) -> AdapterImportResult:
        """Import comments from a source into adapter-neutral records."""

    @abstractmethod
    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> ImportedCommentRecord:
        """Normalize one adapter payload into the canonical import record."""
