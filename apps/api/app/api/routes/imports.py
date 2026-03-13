from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.jobs.queue import TaskQueue
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.imports import ImportPreviewResponse, ImportResponse, IngestionRunRead
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports")


def _import_service(session: Session) -> ImportService:
    return ImportService(
        ingestion_repository=IngestionRunRepository(session),
        comment_repository=CommentRepository(session),
    )


async def _read_upload(file: UploadFile, *, expected_label: str) -> bytes:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Uploaded {expected_label} is empty.")
    return file_bytes


def _to_import_response(run) -> ImportResponse:
    return ImportResponse(
        ingestion_run_id=run.id,
        status=run.status,
        imported_rows=run.imported_rows,
        duplicate_rows=run.duplicate_rows,
        failed_rows=run.failed_rows,
    )


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_import(
    file: UploadFile = File(...),
    session: Session = Depends(db_session),
) -> ImportPreviewResponse:
    file_bytes = await _read_upload(file, expected_label="file")
    filename = file.filename or "comments.json"
    try:
        return _import_service(session).preview_upload_bytes(file_bytes=file_bytes, filename=filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/csv", response_model=ImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_csv(
    file: UploadFile = File(...),
    session: Session = Depends(db_session),
) -> ImportResponse:
    file_bytes = await _read_upload(file, expected_label="CSV")
    try:
        run = _import_service(session).import_csv_bytes(file_bytes=file_bytes, filename=file.filename or "comments.csv")
        session.commit()
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    TaskQueue().enqueue_ingestion_run(str(run.id))
    session.refresh(run)
    return _to_import_response(run)


@router.post("/json", response_model=ImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_json(
    file: UploadFile = File(...),
    session: Session = Depends(db_session),
) -> ImportResponse:
    file_bytes = await _read_upload(file, expected_label="JSON")
    try:
        run = _import_service(session).import_json_bytes(file_bytes=file_bytes, filename=file.filename or "comments.json")
        session.commit()
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    TaskQueue().enqueue_ingestion_run(str(run.id))
    session.refresh(run)
    return _to_import_response(run)


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
