from __future__ import annotations

import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, inspect, pool, text
from sqlalchemy.engine import make_url

from app.core.config import get_settings
import app.db.base  # noqa: F401
from app.models.base import Base

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
logger = logging.getLogger(__name__)

LEGACY_REVISION_ALIASES = {
    "0002_hosted_deployment_ingestion_artifacts": "0002_hosted_ingestion_artifacts",
}

EXPECTED_TABLES = (
    "alembic_version",
    "ingestion_runs",
    "raw_comments",
    "normalized_comments",
    "comment_classifications",
    "mvp_signals",
    "signal_comment_links",
)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        url = make_url(settings.database_url)
        current_database = connection.execute(text("SELECT current_database()")).scalar_one()
        current_schema = connection.execute(text("SELECT current_schema()")).scalar_one()
        search_path = connection.execute(text("SHOW search_path")).scalar_one()
        inspector = inspect(connection)
        before_count = sum(1 for table_name in EXPECTED_TABLES if inspector.has_table(table_name))

        logger.warning(
            "Alembic preflight: driver=%s host=%s port=%s database=%s current_database=%s current_schema=%s search_path=%s matching_tables=%s",
            url.drivername,
            url.host,
            url.port,
            url.database,
            current_database,
            current_schema,
            search_path,
            before_count,
        )

        if inspect(connection).has_table("alembic_version"):
            current_revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
            replacement_revision = LEGACY_REVISION_ALIASES.get(current_revision)
            if replacement_revision:
                connection.execute(
                    text("UPDATE alembic_version SET version_num = :replacement_revision WHERE version_num = :current_revision"),
                    {"replacement_revision": replacement_revision, "current_revision": current_revision},
                )
                connection.commit()

        # SQLAlchemy 2.x opens an implicit transaction for the preflight reads
        # above. Commit it before Alembic starts its own migration transaction
        # so DDL doesn't get rolled back when this connection closes.
        if connection.in_transaction():
            connection.commit()

        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()

        inspector = inspect(connection)
        after_count = sum(1 for table_name in EXPECTED_TABLES if inspector.has_table(table_name))
        current_revision = None
        if inspector.has_table("alembic_version"):
            current_revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()

        logger.warning(
            "Alembic postflight: current_database=%s current_schema=%s search_path=%s matching_tables=%s revision=%s",
            current_database,
            current_schema,
            search_path,
            after_count,
            current_revision,
        )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
