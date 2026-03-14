from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, BinaryIO

from app.adapters.base import AdapterImportFailure, AdapterImportResult, BaseIngestionAdapter, CanonicalCommentObject
from app.models.enums import ImportFormat, IngestionSourceType, SourcePlatform


@dataclass(slots=True)
class JsonPayloadInspection:
    import_format: ImportFormat
    detected_shape: str
    records: list[dict[str, Any]]
    parse_warnings: list[str] = field(default_factory=list)


class TikTokJsonImportAdapter(BaseIngestionAdapter):
    """Parses TikTok export and portability JSON files into canonical comment objects."""

    source_type = IngestionSourceType.JSON_UPLOAD
    source_platform = SourcePlatform.TIKTOK

    def fetch_comments(self, file_content: bytes | str | BinaryIO) -> list[dict[str, Any]]:
        payload = self._load_json(file_content)
        return self.inspect_payload(payload).records

    def import_comments(self, file_content: bytes | str | BinaryIO) -> AdapterImportResult:
        payload = self._load_json(file_content)
        inspection = self.inspect_payload(payload)
        comments: list[CanonicalCommentObject] = []
        failures: list[AdapterImportFailure] = []

        for index, row in enumerate(inspection.records, start=1):
            try:
                comments.append(self.normalize_payload(row, row_number=index))
            except Exception as exc:
                failures.append(
                    AdapterImportFailure(
                        row_number=index,
                        error=str(exc),
                        raw_payload=dict(row),
                    )
                )

        parse_warnings = list(inspection.parse_warnings)
        parse_warnings.extend(
            warning
            for comment in comments
            for warning in comment.parse_warnings
            if warning not in parse_warnings
        )

        return AdapterImportResult(
            source_type=self.source_type,
            source_platform=self.source_platform,
            import_format=inspection.import_format,
            detected_shape=inspection.detected_shape,
            comments=comments,
            failures=failures,
            parse_warnings=parse_warnings,
        )

    def normalize_payload(self, payload: dict[str, Any], row_number: int | None = None) -> CanonicalCommentObject:
        source_video_id = self._first_value(
            payload,
            ["source_video_id", "video_id", "video.id", "video.video_id", "Video ID", "videoId"],
        )
        source_comment_id = self._first_value(
            payload,
            ["source_comment_id", "comment_id", "id", "comment.id", "commentId", "Comment ID"],
        )
        source_parent_comment_id = self._first_value(
            payload,
            ["source_parent_comment_id", "parent_comment_id", "parent_id", "comment.parent_comment_id"],
        )
        author_handle = self._first_value(
            payload,
            [
                "author_handle",
                "author_handle_name",
                "author.unique_id",
                "author.username",
                "user.unique_id",
                "user.username",
                "handle",
                "username",
                "Author",
            ],
        )
        comment_text = self._first_value(
            payload,
            ["comment_text", "text", "comment_text_value", "comment", "comment.text", "content", "Comment"],
        )
        if not comment_text:
            raise ValueError("JSON comment export is missing comment_text/text.")

        parse_warnings: list[str] = []
        if not source_comment_id:
            source_comment_id = self._generated_comment_id(payload=payload, row_number=row_number)
            parse_warnings.append("source_comment_id missing in JSON payload; generated a surrogate identifier.")

        comment_created_at = self._parse_datetime(
            self._first_value(
                payload,
                ["created_at", "create_time", "comment_created_at", "timestamp", "date", "Date", "createTime"],
            )
        )
        if comment_created_at is None:
            parse_warnings.append("comment_created_at missing or not parseable.")
        if not source_video_id:
            parse_warnings.append("source_video_id missing in JSON payload.")

        return CanonicalCommentObject(
            platform=self.source_platform,
            source_type="portability_export" if self._looks_like_portability_record(payload) else "json_export",
            source_video_id=self._clean_string(source_video_id),
            source_comment_id=self._clean_string(source_comment_id) or self._generated_comment_id(payload, row_number),
            source_parent_comment_id=self._clean_string(source_parent_comment_id),
            author_handle=self._clean_string(author_handle),
            comment_text=str(comment_text).strip(),
            comment_created_at=comment_created_at,
            like_count=int(self._first_value(payload, ["like_count", "likes", "digg_count", "stats.like_count"], default=0) or 0),
            reply_count=int(
                self._first_value(payload, ["reply_count", "replies", "reply_comment_total", "stats.reply_count"], default=0)
                or 0
            ),
            raw_payload=dict(payload),
            row_number=row_number,
            parse_warnings=parse_warnings,
        )

    def inspect_payload(self, payload: Any) -> JsonPayloadInspection:
        if isinstance(payload, list):
            records = [item for item in payload if isinstance(item, dict)]
            if not records:
                raise ValueError("JSON export must contain an array of comment objects.")
            return JsonPayloadInspection(
                import_format=ImportFormat.TIKTOK_JSON,
                detected_shape="top_level_array",
                records=records,
                parse_warnings=self._skipped_item_warnings(total_items=len(payload), parsed_items=len(records)),
            )

        if not isinstance(payload, dict):
            raise ValueError("JSON export must be an object or array of comment objects.")

        activity_payload = payload.get("Activity") if isinstance(payload.get("Activity"), dict) else payload.get("activity")
        if isinstance(activity_payload, dict):
            portability_records = activity_payload.get("Comments") or activity_payload.get("comments")
            if isinstance(portability_records, list):
                records = [item for item in portability_records if isinstance(item, dict)]
                if records:
                    return JsonPayloadInspection(
                        import_format=ImportFormat.PORTABILITY_JSON,
                        detected_shape="activity.comments",
                        records=records,
                        parse_warnings=self._skipped_item_warnings(
                            total_items=len(portability_records),
                            parsed_items=len(records),
                        ),
                    )

        comment_payload = payload.get("Comment") if isinstance(payload.get("Comment"), dict) else payload.get("comment")
        if isinstance(comment_payload, dict):
            comments_wrapper = comment_payload.get("Comments") or comment_payload.get("comments")
            if isinstance(comments_wrapper, dict):
                portability_records = (
                    comments_wrapper.get("CommentsList")
                    or comments_wrapper.get("comments_list")
                    or comments_wrapper.get("comments")
                )
                if isinstance(portability_records, list):
                    records = [item for item in portability_records if isinstance(item, dict)]
                    if records:
                        return JsonPayloadInspection(
                            import_format=ImportFormat.PORTABILITY_JSON,
                            detected_shape="comment.comments.comments_list",
                            records=records,
                            parse_warnings=self._skipped_item_warnings(
                                total_items=len(portability_records),
                                parsed_items=len(records),
                            ),
                        )

        for field_name, shape in (("comments", "comments_array"), ("comment_list", "comment_list"), ("Comments", "comments_array")):
            rows = payload.get(field_name)
            if isinstance(rows, list):
                records = [item for item in rows if isinstance(item, dict)]
                if records:
                    import_format = ImportFormat.PORTABILITY_JSON if any(self._looks_like_portability_record(item) for item in records) else ImportFormat.TIKTOK_JSON
                    return JsonPayloadInspection(
                        import_format=import_format,
                        detected_shape=shape,
                        records=records,
                        parse_warnings=self._skipped_item_warnings(total_items=len(rows), parsed_items=len(records)),
                    )

        raise ValueError(
            "Unsupported TikTok JSON shape. Expected a comments array, portability Activity -> Comments wrapper, "
            "TikTok portability Comment -> Comments -> CommentsList wrapper, or a top-level array of comment objects."
        )

    def _load_json(self, file_content: bytes | str | BinaryIO) -> Any:
        if hasattr(file_content, "read"):
            raw = file_content.read()
            content = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
        elif isinstance(file_content, bytes):
            content = file_content.decode("utf-8-sig")
        else:
            content = file_content
        return json.loads(content)

    def _first_value(self, payload: dict[str, Any], paths: list[str], default: Any = None) -> Any:
        for path in paths:
            value: Any = payload
            found = True
            for part in path.split("."):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    found = False
                    break
            if found and value not in (None, ""):
                return value
        return default

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=UTC)
        if isinstance(value, str) and value.isdigit():
            numeric = float(value)
            if len(value) > 10:
                numeric = numeric / 1000
            return datetime.fromtimestamp(numeric, tz=UTC)
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None

    def _clean_string(self, value: Any) -> str | None:
        if value in (None, ""):
            return None
        cleaned = str(value).strip()
        return cleaned or None

    def _looks_like_portability_record(self, payload: dict[str, Any]) -> bool:
        keys = {key.lower() for key in payload}
        return bool({"date", "comment"} & keys) and "id" not in keys and "comment_id" not in keys

    def _generated_comment_id(self, payload: dict[str, Any], row_number: int | None) -> str:
        text = self._first_value(payload, ["comment_text", "text", "comment", "Comment"], default="") or ""
        created_at = self._first_value(payload, ["created_at", "create_time", "date", "Date"], default="") or ""
        digest = hashlib.sha1(f"{text}|{created_at}|{row_number or 0}".encode("utf-8")).hexdigest()[:12]
        return f"generated-{digest}"

    def _skipped_item_warnings(self, *, total_items: int, parsed_items: int) -> list[str]:
        skipped = total_items - parsed_items
        if skipped <= 0:
            return []
        return [f"Skipped {skipped} non-object entries while parsing the JSON payload."]


JsonImportAdapter = TikTokJsonImportAdapter
