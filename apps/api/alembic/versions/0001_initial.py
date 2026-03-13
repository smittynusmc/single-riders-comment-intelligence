"""initial comment intelligence schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-12 21:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

source_platform = sa.Enum(
    "tiktok",
    "instagram",
    "discord",
    "app_store",
    "manual",
    "generic_social",
    "unknown",
    name="sourceplatform",
)
ingestion_source_type = sa.Enum(
    "json_upload",
    "csv_upload",
    "manual_paste",
    "third_party_export",
    "research_api",
    "connector_placeholder",
    name="ingestionsourcetype",
)
import_format = sa.Enum(
    "tiktok_json",
    "csv",
    "research_api_json",
    "portability_json",
    "manual_text",
    "third_party_export",
    name="importformat",
)
ingestion_status = sa.Enum("pending", "imported", "processing", "completed", "failed", name="ingestionstatus")
normalization_status = sa.Enum("pending", "normalized", "skipped_duplicate", "failed", name="normalizationstatus")
classification_status = sa.Enum(
    "pending",
    "classified",
    "needs_review",
    "approved",
    "false_positive",
    name="classificationstatus",
)
signal_status = sa.Enum("active", "reviewed", "archived", name="signalstatus")
primary_category = sa.Enum(
    "feature_request",
    "bug_or_quality",
    "safety_or_trust",
    "moderation_or_bot",
    "social_coordination",
    "confusion_or_onboarding",
    "praise_or_delight",
    "pricing_or_value",
    "other",
    name="primarycategory",
)
mvp_area = sa.Enum(
    "matching",
    "meetups",
    "safety",
    "onboarding",
    "profiles",
    "moderation",
    "messaging",
    "monetization",
    "passholders",
    "community",
    "operations",
    "other",
    name="mvparea",
)
sentiment_label = sa.Enum("positive", "neutral", "negative", "mixed", name="sentimentlabel")


def upgrade() -> None:
    bind = op.get_bind()
    source_platform.create(bind, checkfirst=True)
    ingestion_source_type.create(bind, checkfirst=True)
    import_format.create(bind, checkfirst=True)
    ingestion_status.create(bind, checkfirst=True)
    normalization_status.create(bind, checkfirst=True)
    classification_status.create(bind, checkfirst=True)
    signal_status.create(bind, checkfirst=True)
    primary_category.create(bind, checkfirst=True)
    mvp_area.create(bind, checkfirst=True)
    sentiment_label.create(bind, checkfirst=True)

    op.create_table(
        "ingestion_runs",
        sa.Column("source_type", ingestion_source_type, nullable=False),
        sa.Column("source_platform", source_platform, nullable=False),
        sa.Column("import_format", import_format, nullable=False),
        sa.Column("source_label", sa.String(length=255), nullable=False),
        sa.Column("status", ingestion_status, nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("run_metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "raw_comments",
        sa.Column("ingestion_run_id", sa.Uuid(), nullable=False),
        sa.Column("source_platform", source_platform, nullable=False),
        sa.Column("source_video_id", sa.String(length=255), nullable=True),
        sa.Column("source_comment_id", sa.String(length=255), nullable=False),
        sa.Column("source_parent_comment_id", sa.String(length=255), nullable=True),
        sa.Column("author_handle", sa.String(length=255), nullable=True),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("comment_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reply_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "normalized_comments",
        sa.Column("raw_comment_id", sa.Uuid(), nullable=False),
        sa.Column("ingestion_run_id", sa.Uuid(), nullable=False),
        sa.Column("source_platform", source_platform, nullable=False),
        sa.Column("source_video_id", sa.String(length=255), nullable=True),
        sa.Column("source_comment_id", sa.String(length=255), nullable=False),
        sa.Column("source_parent_comment_id", sa.String(length=255), nullable=True),
        sa.Column("author_handle", sa.String(length=255), nullable=True),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("comment_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reply_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalization_status", normalization_status, nullable=False),
        sa.Column("classification_status", classification_status, nullable=False),
        sa.Column("rules_matched", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"]),
        sa.ForeignKeyConstraint(["raw_comment_id"], ["raw_comments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("raw_comment_id"),
        sa.UniqueConstraint("source_platform", "source_comment_id", name="uq_normalized_comment_source"),
    )

    op.create_table(
        "comment_classifications",
        sa.Column("normalized_comment_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("prompt_version", sa.String(length=50), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=False),
        sa.Column("primary_category", primary_category, nullable=False),
        sa.Column("secondary_categories", sa.JSON(), nullable=False),
        sa.Column("mvp_area", mvp_area, nullable=False),
        sa.Column("sentiment", sentiment_label, nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("mvp_relevance_score", sa.Float(), nullable=False),
        sa.Column("urgency_score", sa.Float(), nullable=False),
        sa.Column("needs_human_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("recommended_action", sa.String(length=255), nullable=False),
        sa.Column("rationale_short", sa.Text(), nullable=False),
        sa.Column("review_status", classification_status, nullable=False),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("override_primary_category", primary_category, nullable=True),
        sa.Column("override_mvp_area", mvp_area, nullable=True),
        sa.Column("is_false_positive", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["normalized_comment_id"], ["normalized_comments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_comment_id"),
    )

    op.create_table(
        "mvp_signals",
        sa.Column("fingerprint", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("mvp_area", mvp_area, nullable=False),
        sa.Column("primary_category", primary_category, nullable=False),
        sa.Column("status", signal_status, nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("priority_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sample_comments", sa.JSON(), nullable=False),
        sa.Column("suggested_backlog_action", sa.String(length=255), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(length=255), nullable=True),
        sa.Column("export_metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint"),
    )

    op.create_table(
        "signal_comment_links",
        sa.Column("signal_id", sa.Uuid(), nullable=False),
        sa.Column("normalized_comment_id", sa.Uuid(), nullable=False),
        sa.Column("classification_id", sa.Uuid(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["classification_id"], ["comment_classifications.id"]),
        sa.ForeignKeyConstraint(["normalized_comment_id"], ["normalized_comments.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["mvp_signals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_id", "normalized_comment_id", name="uq_signal_comment_link"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_table("signal_comment_links")
    op.drop_table("mvp_signals")
    op.drop_table("comment_classifications")
    op.drop_table("normalized_comments")
    op.drop_table("raw_comments")
    op.drop_table("ingestion_runs")

    sentiment_label.drop(bind, checkfirst=True)
    mvp_area.drop(bind, checkfirst=True)
    primary_category.drop(bind, checkfirst=True)
    signal_status.drop(bind, checkfirst=True)
    classification_status.drop(bind, checkfirst=True)
    normalization_status.drop(bind, checkfirst=True)
    ingestion_status.drop(bind, checkfirst=True)
    import_format.drop(bind, checkfirst=True)
    ingestion_source_type.drop(bind, checkfirst=True)
    source_platform.drop(bind, checkfirst=True)
