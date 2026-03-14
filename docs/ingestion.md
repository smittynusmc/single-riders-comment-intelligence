# Ingestion

## MVP policy

TikTok JSON export upload is the preferred ingestion method for phase 1. CSV remains supported as a fallback for cleaned manual datasets and compatible third-party exports.

This is intentional. TikTok public OAuth-related APIs do not provide organic comment retrieval, so the product should not rely on OAuth sign-in as an ingestion mechanism.

## Adapter contract

All ingestion adapters follow the same shape:

- `fetch_comments(...)`
- `import_comments(...)`
- `normalize_payload(...)`

Every adapter maps source-specific input into one canonical comment object before persistence.

## Supported import formats

- `tiktok_json`
- `portability_json`
- `research_api_json`
- `csv`

The import run stores both `source_type` and `import_format` so dashboard users can see how a file was interpreted.

## Implemented adapters

### `TikTokJsonImportAdapter`

Supports:

- top-level arrays of comment objects
- objects containing `comments`
- portability-style wrappers such as `Activity -> Comments`
- TikTok download wrappers such as `Comment -> Comments -> CommentsList`

It preserves the original raw JSON payload for every comment and generates clear warnings when optional fields such as `source_video_id` or `comment_created_at` are missing.

### `CsvImportAdapter`

Expected columns:

- `source_video_id`
- `source_comment_id`
- `author_handle`
- `comment_text`
- `created_at`
- `like_count`
- `reply_count`

The adapter validates required fields, converts counts and timestamps, and emits the same canonical comment object used by JSON imports.

### `TikTokResearchAdapter`

Phase 1 does not perform live Research API calls. The adapter only parses manually supplied JSON payloads that already match approved research comment response shapes.

## Preview flow

The imports page uses `POST /imports/preview` before import. The preview response includes:

- detected format
- detected shape
- parsed comment count
- earliest detected comment date
- latest detected comment date
- months represented
- sections detected
- sections ignored for privacy/scope reasons
- sample fields
- missing canonical fields
- parse warnings
- sample comments

This gives the team a quick validation step before an import run is created.

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

## Stage audit metadata

Each import run now records pipeline audit metadata in `ingestion_runs.run_metadata` so the team can compare counts and date spans across stages:

- `json_parsing`
- `raw_comments_persisted`
- `normalized_comments`
- `classification_inputs`
- `classified_comments`

Each stage records:

- total comments seen
- earliest comment date
- latest comment date
- number of months represented

This was added specifically to catch regressions where a multi-month TikTok export appears narrower in the UI than it really is.
