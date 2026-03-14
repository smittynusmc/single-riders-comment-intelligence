from __future__ import annotations

from pathlib import Path
import runpy


def test_alembic_revision_ids_fit_default_version_table() -> None:
    versions_dir = Path(__file__).resolve().parent.parent / "alembic" / "versions"

    for version_file in versions_dir.glob("*.py"):
        revision = runpy.run_path(str(version_file))["revision"]
        assert len(revision) <= 32, f"{version_file.name} revision id exceeds alembic_version varchar(32)"
