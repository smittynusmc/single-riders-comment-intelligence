from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.db.base  # noqa: F401
from app.models.base import Base


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
