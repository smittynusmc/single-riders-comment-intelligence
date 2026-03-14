from __future__ import annotations

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.session import get_db_session


def db_session() -> Iterator[Session]:
    yield from get_db_session()


def authenticated_user_email(request: Request) -> str | None:
    return getattr(request.state, "authenticated_user_email", None)
