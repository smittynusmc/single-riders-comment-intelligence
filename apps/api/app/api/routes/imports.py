from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.jobs.queue import TaskQueue
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.imports import CsvImportResponse, IngestionRunRead
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports")


@router.post("/csv", response_model=CsvImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_csv(
    file: UploadFile = File(...),
    session: Session = Depends(db_session),
) -> CsvImportResponse:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded CSV is empty.")

    import_service = ImportService(
        ingestion_repository=IngestionRunRepository(session),
        comment_repository=CommentRepository(session),
    )
    run = import_service.import_csv_bytes(file_bytes=file_bytes, filename=file.filename or "comments.csv")
    session.commit()

    TaskQueue().enqueue_ingestion_run(str(run.id))
    session.refresh(run)
    return CsvImportResponse(
        ingestion_run_id=run.id,
        status=run.status,
        imported_rows=run.imported_rows,
        duplicate_rows=run.duplicate_rows,
        failed_rows=run.failed_rows,
    )


@router.get("", response_model=PaginatedResponse[IngestionRunRead])
def list_imports(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(db_session),
) -> PaginatedResponse[IngestionRunRead]:
    repository = IngestionRunRepository(session)
    runs, total = repository.list(limit=limit, offset=offset)
    return PaginatedResponse[IngestionRunRead](
        items=[IngestionRunRead.model_validate(run) for run in runs],
        meta=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{run_id}", response_model=IngestionRunRead)
def get_import(run_id: UUID, session: Session = Depends(db_session)) -> IngestionRunRead:
    run = IngestionRunRepository(session).get(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found.")
    return IngestionRunRead.model_validate(run)
