from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Any, BinaryIO

from pydantic import BaseModel, Field

from app.models.enums import ImportFormat, IngestionSourceType, SourcePlatform


class CanonicalCommentObject(BaseModel):
    platform: SourcePlatform = SourcePlatform.TIKTOK
    source_type: str
    source_video_id: str | None = None
    source_comment_id: str
    source_parent_comment_id: str | None = None
    author_handle: str | None = None
    comment_text: str
    comment_created_at: datetime | None = None
    like_count: int = 0
    reply_count: int = 0
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    row_number: int | None = None
    parse_warnings: list[str] = Field(default_factory=list)


ImportedCommentRecord = CanonicalCommentObject


class AdapterImportFailure(BaseModel):
    row_number: int | None = None
    error: str
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class AdapterImportResult(BaseModel):
    source_type: IngestionSourceType
    source_platform: SourcePlatform
    import_format: ImportFormat
    detected_shape: str | None = None
    comments: list[CanonicalCommentObject] = Field(default_factory=list)
    failures: list[AdapterImportFailure] = Field(default_factory=list)
    parse_warnings: list[str] = Field(default_factory=list)

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
        """Import comments from a source into canonical comment objects."""

    @abstractmethod
    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> CanonicalCommentObject:
        """Normalize one adapter payload into the canonical comment object."""