from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.adapters.base import AdapterImportResult, CanonicalCommentObject
from app.adapters.csv_adapter import CsvImportAdapter
from app.adapters.json_adapter import TikTokJsonImportAdapter
from app.adapters.tiktok_research import TikTokResearchAdapter
from app.models.comment import RawComment
from app.models.enums import ImportFormat, IngestionStatus
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.schemas.imports import ImportPreviewResponse, ImportPreviewSample

REQUIRED_CANONICAL_FIELDS = ("source_comment_id", "comment_text")
OPTIONAL_CANONICAL_FIELDS = (
    "source_video_id",
    "source_parent_comment_id",
    "author_handle",
    "comment_created_at",
    "like_count",
    "reply_count",
)
APPROVED_JSON_SECTIONS = {"activity", "comment", "comments", "post"}
logger = logging.getLogger(__name__)


def ensure_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


class ImportService:
    """Persists raw imported comments while keeping adapter concerns isolated."""

    def __init__(self, ingestion_repository: IngestionRunRepository, comment_repository: CommentRepository):
        self.ingestion_repository = ingestion_repository
        self.comment_repository = comment_repository
        self.csv_adapter = CsvImportAdapter()
        self.json_adapter = TikTokJsonImportAdapter()
        self.research_adapter = TikTokResearchAdapter()

    def preview_upload_bytes(self, *, file_bytes: bytes, filename: str) -> ImportPreviewResponse:
        result = self._load_adapter_result(file_bytes=file_bytes, filename=filename)
        comments = result.comments
        sample_payload = comments[0].raw_payload if comments else {}
        sample_fields = self._flatten_payload_keys(sample_payload)
        missing_fields = self._missing_fields(comments[0]) if comments else list(REQUIRED_CANONICAL_FIELDS)
        sections_detected, sections_ignored = self._preview_section_scope(file_bytes=file_bytes, filename=filename)
        earliest_comment_date, latest_comment_date, months_represented = self._comment_date_coverage(comments)
        logger.info(
            "Import preview parsed %s comments spanning %s to %s across %s months from %s",
            len(comments),
            earliest_comment_date.isoformat() if earliest_comment_date else None,
            latest_comment_date.isoformat() if latest_comment_date else None,
            months_represented,
            filename,
        )

        return ImportPreviewResponse(
            detected_format=result.import_format,
            detected_shape=result.detected_shape,
            comment_count=len(comments),
            earliest_comment_date=earliest_comment_date,
            latest_comment_date=latest_comment_date,
            months_represented=months_represented,
            sections_detected=sections_detected,
            sections_ignored=sections_ignored,
            sample_fields=sample_fields,
            missing_fields=missing_fields,
            parse_warnings=result.parse_warnings,
            sample_comments=[
                ImportPreviewSample(
                    source_comment_id=comment.source_comment_id,
                    source_video_id=comment.source_video_id,
                    author_handle=comment.author_handle,
                    comment_text=comment.comment_text,
                    comment_created_at=comment.comment_created_at,
                )
                for comment in comments[:3]
            ],
        )

    def import_csv_bytes(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        content_type: str | None = None,
        uploaded_by_email: str | None = None,
    ):
        return self._persist_adapter_result(
            result=self.csv_adapter.import_comments(file_bytes),
            filename=filename,
            adapter_name="csv",
            file_bytes=file_bytes,
            content_type=content_type,
            uploaded_by_email=uploaded_by_email,
        )

    def import_json_bytes(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        content_type: str | None = None,
        uploaded_by_email: str | None = None,
    ):
        return self._persist_adapter_result(
            result=self._load_adapter_result(file_bytes=file_bytes, filename=filename),
            filename=filename,
            adapter_name="json",
            file_bytes=file_bytes,
            content_type=content_type,
            uploaded_by_email=uploaded_by_email,
        )

    def _load_adapter_result(self, *, file_bytes: bytes, filename: str) -> AdapterImportResult:
        lower_name = filename.lower()
        if lower_name.endswith(".csv"):
            return self.csv_adapter.import_comments(file_bytes)

        if not lower_name.endswith(".json"):
            raise ValueError("Unsupported import type. Upload a TikTok JSON export or a compatible CSV file.")

        errors: list[str] = []
        for adapter in (self.research_adapter, self.json_adapter):
            try:
                return adapter.import_comments(file_bytes)
            except ValueError as exc:
                errors.append(str(exc))

        raise ValueError(
            "Unsupported JSON import shape. Supported inputs include TikTok export comment arrays, "
            "portability activity comment exports, and approved Research API response JSON. "
            f"Details: {' | '.join(errors)}"
        )

    def _persist_adapter_result(
        self,
        *,
        result: AdapterImportResult,
        filename: str,
        adapter_name: str,
        file_bytes: bytes,
        content_type: str | None,
        uploaded_by_email: str | None,
    ):
        parsing_coverage = self._coverage_payload_from_comments(result.comments)
        source_file_sha256 = hashlib.sha256(file_bytes).hexdigest()
        run = self.ingestion_repository.create(
            source_type=result.source_type,
            source_platform=result.source_platform,
            import_format=result.import_format,
            source_label=filename,
            uploaded_by_email=uploaded_by_email,
            source_file_content_type=content_type,
            source_file_size_bytes=len(file_bytes),
            source_file_sha256=source_file_sha256,
            source_file_blob=file_bytes,
            run_metadata={
                "adapter": adapter_name,
                "source_filename": filename,
                "detected_shape": result.detected_shape,
                "parse_warnings": result.parse_warnings,
                "source_artifact": {
                    "storage_backend": "database_blob",
                    "content_type": content_type,
                    "size_bytes": len(file_bytes),
                    "sha256": source_file_sha256,
                },
                "failed_samples": [failure.model_dump() for failure in result.failures[:10]],
                "pipeline_audit": {
                    "json_parsing": parsing_coverage,
                },
            },
            status=IngestionStatus.PENDING,
        )

        known_ids = self.comment_repository.existing_source_comment_ids(
            source_platform=result.source_platform,
            source_comment_ids=[item.source_comment_id for item in result.comments],
        )
        seen_ids = set(known_ids)
        raw_comments: list[RawComment] = []
        duplicate_rows = 0
        imported_rows = 0

        for item in result.comments:
            is_duplicate = item.source_comment_id in seen_ids
            if is_duplicate:
                duplicate_rows += 1
            else:
                imported_rows += 1
                seen_ids.add(item.source_comment_id)

            raw_comments.append(
                RawComment(
                    ingestion_run_id=run.id,
                    source_platform=item.platform,
                    source_video_id=item.source_video_id,
                    source_comment_id=item.source_comment_id,
                    source_parent_comment_id=item.source_parent_comment_id,
                    author_handle=item.author_handle,
                    comment_text=item.comment_text,
                    comment_created_at=item.comment_created_at,
                    like_count=item.like_count,
                    reply_count=item.reply_count,
                    row_number=item.row_number,
                    is_duplicate=is_duplicate,
                    raw_payload_json=item.raw_payload,
                )
            )

        self.comment_repository.create_raw_comments(raw_comments)
        raw_coverage = self._coverage_payload_from_raw_comments(raw_comments)
        run.run_metadata = {
            **dict(run.run_metadata),
            "pipeline_audit": {
                **dict(run.run_metadata.get("pipeline_audit", {})),
                "raw_comments_persisted": {
                    **raw_coverage,
                    "duplicate_rows": duplicate_rows,
                    "imported_rows": imported_rows,
                },
            },
        }
        self.ingestion_repository.apply_summary(
            run,
            total_rows=result.total_rows,
            imported_rows=imported_rows,
            duplicate_rows=duplicate_rows,
            failed_rows=len(result.failures),
            status=IngestionStatus.IMPORTED,
        )
        logger.info(
            "Import persisted %s raw comments spanning %s to %s across %s months from %s",
            raw_coverage["total_comments_seen"],
            raw_coverage["earliest_comment_date"],
            raw_coverage["latest_comment_date"],
            raw_coverage["months_represented"],
            filename,
        )
        return run

    def _flatten_payload_keys(self, payload: dict[str, Any], prefix: str = "", depth: int = 0) -> list[str]:
        if not isinstance(payload, dict) or depth > 2:
            return []

        keys: list[str] = []
        for key, value in payload.items():
            dotted_key = f"{prefix}.{key}" if prefix else key
            keys.append(dotted_key)
            if isinstance(value, dict):
                keys.extend(self._flatten_payload_keys(value, prefix=dotted_key, depth=depth + 1))
        return sorted(dict.fromkeys(keys))

    def _missing_fields(self, comment: CanonicalCommentObject) -> list[str]:
        fields: list[str] = []
        for name in REQUIRED_CANONICAL_FIELDS + OPTIONAL_CANONICAL_FIELDS:
            value = getattr(comment, name, None)
            if value in (None, ""):
                fields.append(name)
        return fields

    def _preview_section_scope(self, *, file_bytes: bytes, filename: str) -> tuple[list[str], list[str]]:
        if not filename.lower().endswith(".json"):
            return [], []

        try:
            payload = json.loads(file_bytes.decode("utf-8-sig"))
        except Exception:
            return [], []

        if not isinstance(payload, dict):
            return [], []

        sections_detected = [str(key) for key in payload.keys()]
        sections_ignored = [section for section in sections_detected if section.lower() not in APPROVED_JSON_SECTIONS]
        return sections_detected, sections_ignored

    def _comment_date_coverage(self, comments: list[CanonicalCommentObject]) -> tuple[datetime | None, datetime | None, int]:
        dates = [ensure_utc(comment.comment_created_at) for comment in comments if comment.comment_created_at is not None]
        if not dates:
            return None, None, 0

        earliest = min(dates)
        latest = max(dates)
        months_represented = len({(value.year, value.month) for value in dates})
        return earliest, latest, months_represented

    def _coverage_payload_from_comments(self, comments: list[CanonicalCommentObject]) -> dict[str, Any]:
        earliest, latest, months_represented = self._comment_date_coverage(comments)
        return {
            "total_comments_seen": len(comments),
            "earliest_comment_date": earliest.isoformat() if earliest else None,
            "latest_comment_date": latest.isoformat() if latest else None,
            "months_represented": months_represented,
        }

    def _coverage_payload_from_raw_comments(self, comments: list[RawComment]) -> dict[str, Any]:
        dates = [ensure_utc(comment.comment_created_at) for comment in comments if comment.comment_created_at is not None]
        earliest = min(dates).isoformat() if dates else None
        latest = max(dates).isoformat() if dates else None
        months_represented = len({(value.year, value.month) for value in dates}) if dates else 0
        return {
            "total_comments_seen": len(comments),
            "earliest_comment_date": earliest,
            "latest_comment_date": latest,
            "months_represented": months_represented,
        }
