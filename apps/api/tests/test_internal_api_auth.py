from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.base  # noqa: F401
from app.api.deps import db_session
from app.main import app, settings
from app.models.base import Base
from app.models.ingestion import IngestionRun

JSON_CONTENT = b"""{
  "comments": [
    {
      "video_id": "video-1",
      "comment_id": "comment-1",
      "user": { "unique_id": "userone" },
      "text": "Need a meetup feature",
      "create_time": "2026-03-01T10:00:00Z",
      "digg_count": 10,
      "reply_comment_total": 2
    }
  ]
}"""


def test_internal_api_token_protects_non_health_routes():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    session: Session = TestingSession()

    def override_db_session():
        try:
            yield session
        finally:
            pass

    previous_token = settings.internal_api_token
    settings.internal_api_token = "shared-service-token"
    app.dependency_overrides[db_session] = override_db_session

    try:
        with TestClient(app) as client:
            unauthorized = client.get("/dashboard/summary")
            authorized = client.get("/dashboard/summary", headers={"x-internal-api-token": "shared-service-token"})
            health = client.get("/health")

        assert unauthorized.status_code == 401
        assert authorized.status_code == 200
        assert health.status_code == 200
    finally:
        settings.internal_api_token = previous_token
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_import_route_records_authenticated_uploader_email():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    session: Session = TestingSession()

    def override_db_session():
        try:
            yield session
        finally:
            pass

    previous_token = settings.internal_api_token
    settings.internal_api_token = "shared-service-token"
    app.dependency_overrides[db_session] = override_db_session

    try:
        with TestClient(app) as client:
            with patch("app.api.routes.imports.TaskQueue.enqueue_ingestion_run", return_value=None):
                response = client.post(
                    "/imports/json",
                    files={"file": ("comments.json", JSON_CONTENT, "application/json")},
                    headers={
                        "x-internal-api-token": "shared-service-token",
                        "x-authenticated-user-email": "adam@example.com",
                    },
                )

        assert response.status_code == 202
        run = session.query(IngestionRun).one()
        assert run.uploaded_by_email == "adam@example.com"
        assert run.source_file_blob == JSON_CONTENT
    finally:
        settings.internal_api_token = previous_token
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)
