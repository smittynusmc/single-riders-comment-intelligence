# Ingestion

## MVP policy

CSV import is the primary ingestion method for phase 1.

This is intentional. TikTok public OAuth-related APIs do not provide organic comment retrieval, so the product should not rely on OAuth sign-in as an ingestion mechanism.

## Adapter contract

All ingestion adapters follow the same shape:

- `fetch_comments(...)`
- `import_comments(...)`
- `normalize_payload(...)`

That keeps the rest of the system independent of where comments came from.

## Implemented adapter

### `CsvImportAdapter`

Expected columns:

- `source_video_id`
- `source_comment_id`
- `author_handle`
- `comment_text`
- `created_at`
- `like_count`
- `reply_count`

The adapter parses rows, validates required fields, converts counts and timestamps, and emits canonical import records for the `ImportService`.

## Placeholder adapters

### `ManualPasteAdapter`

Useful for rapid internal review or small ad hoc datasets.

### `ThirdPartyExportPlaceholderAdapter`

Reserved for approved exports from social listening or community tooling.

### `TikTokConnectorPlaceholderAdapter`

Exists only as a future seam. It should remain unimplemented until an official comment-capable API path is actually available and approved.

## Deduplication policy

- every imported row is stored in `raw_comments`
- duplicates are flagged during import
- canonical processing happens only once in `normalized_comments`

This preserves auditability while keeping the downstream pipeline from double-counting the same source comment.
