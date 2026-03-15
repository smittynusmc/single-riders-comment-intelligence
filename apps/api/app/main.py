from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import bindparam, inspect, text
from sqlalchemy.engine import make_url

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()
logger = logging.getLogger(__name__)

EXPECTED_TABLES = (
    "alembic_version",
    "ingestion_runs",
    "raw_comments",
    "normalized_comments",
    "comment_classifications",
    "mvp_signals",
    "signal_comment_links",
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Internal product intelligence API for social comments and MVP signals.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def log_database_diagnostics() -> None:
    url = make_url(settings.database_url)
    try:
        with engine.connect() as connection:
            current_database = connection.execute(text("SELECT current_database()")).scalar_one()
            current_schema = connection.execute(text("SELECT current_schema()")).scalar_one()
            search_path = connection.execute(text("SHOW search_path")).scalar_one()
            inspector = inspect(connection)
            inspector_matching_tables = sum(1 for table_name in EXPECTED_TABLES if inspector.has_table(table_name))
            matching_tables = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_name IN :table_names
                    """
                ).bindparams(bindparam("table_names", expanding=True)),
                {"table_names": EXPECTED_TABLES},
            ).scalar_one()
            found_tables = connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_name IN :table_names
                    ORDER BY table_name
                    """
                ).bindparams(bindparam("table_names", expanding=True)),
                {"table_names": EXPECTED_TABLES},
            ).scalars().all()
            revision = None
            if connection.execute(text("SELECT to_regclass('public.alembic_version')")).scalar_one():
                revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()

        logger.warning(
            "DB diagnostics: driver=%s host=%s port=%s database=%s current_database=%s current_schema=%s search_path=%s inspector_matching_tables=%s information_schema_matching_tables=%s revision=%s found_tables=%s",
            url.drivername,
            url.host,
            url.port,
            url.database,
            current_database,
            current_schema,
            search_path,
            inspector_matching_tables,
            matching_tables,
            revision,
            found_tables,
        )
    except Exception:
        logger.exception("DB diagnostics failed during startup.")


@app.middleware("http")
async def require_internal_api_token(request: Request, call_next):
    if request.url.path == "/health" or not settings.internal_api_token:
        return await call_next(request)

    if request.headers.get("x-internal-api-token") != settings.internal_api_token:
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid internal API token."})

    request.state.authenticated_user_email = request.headers.get("x-authenticated-user-email")
    return await call_next(request)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
