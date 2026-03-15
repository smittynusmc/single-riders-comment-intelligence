from __future__ import annotations

from pathlib import Path
import runpy

from app.models.classification import CommentClassification
from app.models.comment import NormalizedComment, RawComment
from app.models.enums import (
    ClassificationStatus,
    ImportFormat,
    IngestionSourceType,
    IngestionStatus,
    MvpArea,
    NormalizationStatus,
    PrimaryCategory,
    SentimentLabel,
    SignalStatus,
    SourcePlatform,
)
from app.models.ingestion import IngestionRun
from app.models.signal import MvpSignal


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


def test_models_persist_enum_values_instead_of_member_names() -> None:
    assert IngestionRun.__table__.c.source_type.type.enums == [member.value for member in IngestionSourceType]
    assert IngestionRun.__table__.c.source_platform.type.enums == [member.value for member in SourcePlatform]
    assert IngestionRun.__table__.c.import_format.type.enums == [member.value for member in ImportFormat]
    assert IngestionRun.__table__.c.status.type.enums == [member.value for member in IngestionStatus]
    assert RawComment.__table__.c.source_platform.type.enums == [member.value for member in SourcePlatform]
    assert NormalizedComment.__table__.c.normalization_status.type.enums == [member.value for member in NormalizationStatus]
    assert NormalizedComment.__table__.c.classification_status.type.enums == [member.value for member in ClassificationStatus]
    assert CommentClassification.__table__.c.primary_category.type.enums == [member.value for member in PrimaryCategory]
    assert CommentClassification.__table__.c.mvp_area.type.enums == [member.value for member in MvpArea]
    assert CommentClassification.__table__.c.sentiment.type.enums == [member.value for member in SentimentLabel]
    assert MvpSignal.__table__.c.status.type.enums == [member.value for member in SignalStatus]
