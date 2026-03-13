# Architecture

## Purpose

The system turns imported social comments into grouped MVP signals for Single Riders backlog planning. It is intentionally designed as an internal product tool rather than a public app feature.

## Non-goals in phase 1

- No TikTok OAuth ingestion path
- No undocumented TikTok comment scraping or hidden API assumptions
- No one-backlog-item-per-comment workflow
- No public-facing end user UI

## Core pipeline

```text
TikTok JSON export / portability JSON / research response JSON / CSV fallback
  -> ingestion adapter
  -> ingestion_runs + raw_comments
  -> normalization service
  -> rules pre-pass
  -> configurable classifier
  -> comment_classifications
  -> signal aggregation
  -> mvp_signals + signal_comment_links
  -> admin API
  -> internal dashboard / export placeholders
```

## Why adapters first

TikTok access for comment retrieval is not stable or generally available through public OAuth-based APIs, so export-based ingestion is the safer default. The ingestion layer is therefore built around neutral adapters rather than platform-specific logic inside services.

Implemented now:

- `TikTokJsonImportAdapter`
- `CsvImportAdapter`
- `TikTokResearchAdapter` for manually supplied approved research response JSON

Included as placeholders for future work:

- `ManualPasteAdapter`
- `ThirdPartyExportPlaceholderAdapter`
- `TikTokConnectorPlaceholderAdapter`

## Canonical comment contract

All adapters emit the same internal comment object before anything is persisted or classified.

```json
{
  "platform": "tiktok",
  "source_type": "json_export",
  "source_video_id": "string|null",
  "source_comment_id": "string",
  "source_parent_comment_id": "string|null",
  "author_handle": "string|null",
  "comment_text": "string",
  "comment_created_at": "ISO-8601|null",
  "like_count": 0,
  "reply_count": 0,
  "raw_payload": {}
}
```

This keeps the rest of the system independent of whether the original source was a TikTok export, a research response JSON file, or a CSV convenience import.

## Persistence model

### `ingestion_runs`

Tracks adapter source, import format, counts, status, detected shape, warnings, and failure metadata.

### `raw_comments`

Stores untouched imported comments and the original `raw_payload_json` for auditing and replay.

### `normalized_comments`

Stores canonicalized text plus rule tags and pipeline status.

### `comment_classifications`

Stores the structured AI output, review overrides, and false-positive flags.

### `mvp_signals`

Stores grouped signal summaries, sample comments, and priority scores.

### `signal_comment_links`

Stores the evidence mapping between grouped signals and comment classifications.

## Service boundaries

- `ImportService`: adapter orchestration, preview summaries, and raw persistence
- `NormalizationService`: canonical text cleanup and rule tagging
- `KeywordRuleService`: deterministic pre-pass for obvious keywords
- `CommentClassificationService`: structured classification with provider abstraction
- `SignalAggregationService`: converts many classified comments into a smaller ranked signal set
- `DashboardService`: summary, trends, and signal read models for the frontend
- `ExportService`: safe placeholders for GitHub, Trello, and docs export flows

## Worker model

The API stores imported raw comments first, then enqueues processing. In phase 1 the queue is configurable:

- `SCI_WORKER_MODE=inline` for simpler local workflows
- `SCI_WORKER_MODE=rq` for Redis-backed asynchronous processing

That setting is explicit so import endpoints do not hide how work is executed.

## Classification design

The classifier expects structured JSON only. The backend validates model output against a Pydantic schema before it is persisted.

Required fields:

- `primary_category`
- `secondary_categories`
- `mvp_area`
- `sentiment`
- `confidence`
- `mvp_relevance_score`
- `urgency_score`
- `needs_human_review`
- `recommended_action`
- `rationale_short`

Rules can short-circuit the model entirely for obvious cases such as safety or bot concerns.

## Signal aggregation strategy

Phase 1 uses deterministic fingerprinting based on:

- effective MVP area
- effective primary category
- matched rule tags
- normalized keyword signature

This keeps the implementation understandable while leaving room for future embedding-based clustering if the comment volume demands it.
