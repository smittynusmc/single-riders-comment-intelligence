from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, inspect, pool, text

from app.core.config import get_settings
import app.db.base  # noqa: F401
from app.models.base import Base

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

LEGACY_REVISION_ALIASES = {
    "0002_hosted_deployment_ingestion_artifacts": "0002_hosted_ingestion_artifacts",
}


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
        if inspect(connection).has_table("alembic_version"):
            current_revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
            replacement_revision = LEGACY_REVISION_ALIASES.get(current_revision)
            if replacement_revision:
                connection.execute(
                    text("UPDATE alembic_version SET version_num = :replacement_revision WHERE version_num = :current_revision"),
                    {"replacement_revision": replacement_revision, "current_revision": current_revision},
                )
                connection.commit()

        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
