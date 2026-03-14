from __future__ import annotations

import os

import uvicorn

import app.db.base  # noqa: F401
from app.db.session import engine
from app.main import app as fastapi_app
from app.models.base import Base


def main() -> None:
    Base.metadata.create_all(bind=engine)

    host = os.environ.get("SCI_API_HOST", "127.0.0.1")
    port = int(os.environ.get("SCI_API_PORT", "8000"))

    uvicorn.run(fastapi_app, host=host, port=port)


if __name__ == "__main__":
    main()
