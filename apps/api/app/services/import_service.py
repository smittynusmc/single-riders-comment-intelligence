from __future__ import annotations

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

        return ImportPreviewResponse(
            detected_format=result.import_format,
            detected_shape=result.detected_shape,
            comment_count=len(comments),
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

    def import_csv_bytes(self, *, file_bytes: bytes, filename: str):
        return self._persist_adapter_result(
            result=self.csv_adapter.import_comments(file_bytes),
            filename=filename,
            adapter_name="csv",
        )

    def import_json_bytes(self, *, file_bytes: bytes, filename: str):
        return self._persist_adapter_result(
            result=self._load_adapter_result(file_bytes=file_bytes, filename=filename),
            filename=filename,
            adapter_name="json",
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

    def _persist_adapter_result(self, *, result: AdapterImportResult, filename: str, adapter_name: str):
        run = self.ingestion_repository.create(
            source_type=result.source_type,
            source_platform=result.source_platform,
            import_format=result.import_format,
            source_label=filename,
            run_metadata={
                "adapter": adapter_name,
                "source_filename": filename,
                "detected_shape": result.detected_shape,
                "parse_warnings": result.parse_warnings,
                "failed_samples": [failure.model_dump() for failure in result.failures[:10]],
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
        self.ingestion_repository.apply_summary(
            run,
            total_rows=result.total_rows,
            imported_rows=imported_rows,
            duplicate_rows=duplicate_rows,
            failed_rows=len(result.failures),
            status=IngestionStatus.IMPORTED,
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
