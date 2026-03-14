from __future__ import annotations

from pathlib import Path
import runpy


def test_initial_migration_uses_non_creating_postgres_enums() -> None:
    migration_globals = runpy.run_path(str(Path(__file__).resolve().parent.parent / "alembic" / "versions" / "0001_initial.py"))

    enum_names = [
        "source_platform",
        "ingestion_source_type",
        "import_format",
        "ingestion_status",
        "normalization_status",
        "classification_status",
        "signal_status",
        "primary_category",
        "mvp_area",
        "sentiment_label",
    ]

    for enum_name in enum_names:
        enum_type = migration_globals[enum_name]
        assert getattr(enum_type, "create_type", None) is False
