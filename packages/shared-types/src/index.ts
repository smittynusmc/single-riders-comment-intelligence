export type SourcePlatform =
  | "tiktok"
  | "instagram"
  | "discord"
  | "app_store"
  | "manual"
  | "generic_social"
  | "unknown";

export type IngestionSourceType =
  | "json_upload"
  | "csv_upload"
  | "manual_paste"
  | "third_party_export"
  | "research_api"
  | "connector_placeholder";

export type ImportFormat =
  | "tiktok_json"
  | "csv"
  | "research_api_json"
  | "portability_json"
  | "manual_text"
  | "third_party_export";

export type IngestionStatus = "pending" | "imported" | "processing" | "completed" | "failed";
export type ClassificationStatus = "pending" | "classified" | "needs_review" | "approved" | "false_positive";
export type NormalizationStatus = "pending" | "normalized" | "skipped_duplicate" | "failed";
export type SignalStatus = "active" | "reviewed" | "archived";
export type PrimaryCategory =
  | "feature_request"
  | "bug_or_quality"
  | "safety_or_trust"
  | "moderation_or_bot"
  | "social_coordination"
  | "confusion_or_onboarding"
  | "praise_or_delight"
  | "pricing_or_value"
  | "other";
export type MvpArea =
  | "matching"
  | "meetups"
  | "safety"
  | "onboarding"
  | "profiles"
  | "moderation"
  | "messaging"
  | "monetization"
  | "passholders"
  | "community"
  | "operations"
  | "other";
export type Sentiment = "positive" | "neutral" | "negative" | "mixed";

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PaginationMeta;
}

export interface IngestionRun {
  id: string;
  source_type: IngestionSourceType;
  source_platform: SourcePlatform;
  import_format: ImportFormat;
  source_label: string;
  status: IngestionStatus;
  total_rows: number;
  imported_rows: number;
  duplicate_rows: number;
  failed_rows: number;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
  uploaded_by_email: string | null;
  source_file_content_type: string | null;
  source_file_size_bytes: number | null;
  source_file_sha256: string | null;
  run_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RawComment {
  id: string;
  ingestion_run_id: string;
  source_platform: SourcePlatform;
  source_video_id: string | null;
  source_comment_id: string;
  source_parent_comment_id: string | null;
  author_handle: string | null;
  comment_text: string;
  comment_created_at: string | null;
  like_count: number;
  reply_count: number;
  row_number: number | null;
  is_duplicate: boolean;
  raw_payload_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface NormalizedComment {
  id: string;
  raw_comment_id: string;
  ingestion_run_id: string;
  source_platform: SourcePlatform;
  source_video_id: string | null;
  source_comment_id: string;
  source_parent_comment_id: string | null;
  author_handle: string | null;
  original_text: string;
  normalized_text: string;
  comment_created_at: string | null;
  like_count: number;
  reply_count: number;
  normalization_status: NormalizationStatus;
  classification_status: ClassificationStatus;
  rules_matched: string[];
  created_at: string;
  updated_at: string;
}

export interface CommentClassification {
  id: string;
  normalized_comment_id: string;
  provider: string;
  model_name: string;
  prompt_version: string;
  primary_category: PrimaryCategory;
  secondary_categories: string[];
  mvp_area: MvpArea;
  sentiment: Sentiment;
  confidence: number;
  mvp_relevance_score: number;
  urgency_score: number;
  needs_human_review: boolean;
  recommended_action: string;
  rationale_short: string;
  review_status: ClassificationStatus;
  reviewer_note: string | null;
  reviewed_at: string | null;
  override_primary_category: PrimaryCategory | null;
  override_mvp_area: MvpArea | null;
  is_false_positive: boolean;
  created_at: string;
  updated_at: string;
}

export interface CommentItem {
  raw_comment: RawComment;
  normalized_comment: NormalizedComment | null;
  classification: CommentClassification | null;
}

export interface ClassificationReviewContext {
  id: string;
  source_video_id: string | null;
  source_comment_id: string;
  author_handle: string | null;
  original_text: string;
  normalized_text: string;
  comment_created_at: string | null;
  like_count: number;
  reply_count: number;
  rules_matched: string[];
}

export interface ClassificationReviewItem {
  classification: CommentClassification;
  normalized_comment: ClassificationReviewContext;
}

export interface SignalCommentEvidence {
  normalized_comment_id: string;
  classification_id: string | null;
  comment_text: string;
  author_handle: string | null;
  relevance_score: number;
}

export interface Signal {
  id: string;
  fingerprint: string;
  title: string;
  summary: string;
  mvp_area: MvpArea;
  primary_category: PrimaryCategory;
  status: SignalStatus;
  evidence_count: number;
  priority_score: number;
  first_seen_at: string | null;
  last_seen_at: string | null;
  sample_comments: Array<Record<string, unknown>>;
  suggested_backlog_action: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  export_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SignalDetail extends Signal {
  linked_comments: SignalCommentEvidence[];
}

export interface SignalExportResponse {
  signal_id: string;
  destination: string;
  status: string;
  reference: string | null;
}

export interface BreakdownItem {
  key: string;
  count: number;
}

export interface VideoInsightItem {
  key: string;
  label: string;
  comment_count: number;
  average_priority_score: number;
  top_theme: string | null;
}

export interface AudienceThemeInsight {
  key: string;
  label: string;
  summary: string;
  story_anchor: string;
  evidence_count: number;
  weighted_score: number;
  recent_evidence_count: number;
  momentum: number;
  trend_label: string;
  mvp_area: MvpArea | null;
  primary_category: PrimaryCategory | null;
  sample_comments: string[];
}

export interface AudienceInsights {
  mvp_priorities: AudienceThemeInsight[];
  user_concerns: AudienceThemeInsight[];
  confusion_points: AudienceThemeInsight[];
  positive_validation: AudienceThemeInsight[];
  story_alignment: AudienceThemeInsight[];
  top_videos: VideoInsightItem[];
}

export interface DashboardSummary {
  total_comments: number;
  comments_this_week: number;
  needs_review_count: number;
  total_signals: number;
  earliest_comment_date: string | null;
  latest_comment_date: string | null;
  months_represented: number;
  top_categories: BreakdownItem[];
  top_mvp_areas: BreakdownItem[];
  top_repeated_requests: BreakdownItem[];
  top_safety_concerns: BreakdownItem[];
  top_user_concerns: BreakdownItem[];
  top_confusion_points: BreakdownItem[];
  top_positive_validation: BreakdownItem[];
}

export interface TrendPoint {
  bucket: string;
  comments: number;
  review_queue: number;
}

export interface TopSignalSummary {
  id: string;
  title: string;
  mvp_area: string;
  evidence_count: number;
  priority_score: number;
}

export interface ImportPreviewSample {
  source_comment_id: string;
  source_video_id: string | null;
  author_handle: string | null;
  comment_text: string;
  comment_created_at: string | null;
}

export interface ImportPreview {
  detected_format: ImportFormat;
  detected_shape: string | null;
  comment_count: number;
  earliest_comment_date: string | null;
  latest_comment_date: string | null;
  months_represented: number;
  sections_detected: string[];
  sections_ignored: string[];
  sample_fields: string[];
  missing_fields: string[];
  parse_warnings: string[];
  sample_comments: ImportPreviewSample[];
}
