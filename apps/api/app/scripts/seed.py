from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

import app.db.base  # noqa: F401
from app.models.base import Base
from app.db.session import SessionLocal, engine
from app.jobs.queue import TaskQueue
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.services.import_service import ImportService


def seed_from_sample_export() -> None:
    Base.metadata.create_all(bind=engine)
    sample_path = Path(__file__).resolve().parents[4] / "sample_data" / "tiktok_comments_sample.json"
    file_bytes = sample_path.read_bytes()

    session: Session = SessionLocal()
    try:
        service = ImportService(IngestionRunRepository(session), CommentRepository(session))
        run = service.import_json_bytes(file_bytes=file_bytes, filename=sample_path.name)
        session.commit()
        TaskQueue().enqueue_ingestion_run(str(run.id))
        print(f"Seeded import run {run.id}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_from_sample_export()