"""add hosted deployment ingestion artifact fields

Revision ID: 0002_hosted_deployment_ingestion_artifacts
Revises: 0001_initial
Create Date: 2026-03-14 18:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_hosted_deployment_ingestion_artifacts"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_runs", sa.Column("uploaded_by_email", sa.String(length=255), nullable=True))
    op.add_column("ingestion_runs", sa.Column("source_file_content_type", sa.String(length=255), nullable=True))
    op.add_column("ingestion_runs", sa.Column("source_file_size_bytes", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("source_file_sha256", sa.String(length=64), nullable=True))
    op.add_column("ingestion_runs", sa.Column("source_file_blob", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("ingestion_runs", "source_file_blob")
    op.drop_column("ingestion_runs", "source_file_sha256")
    op.drop_column("ingestion_runs", "source_file_size_bytes")
    op.drop_column("ingestion_runs", "source_file_content_type")
    op.drop_column("ingestion_runs", "uploaded_by_email")

