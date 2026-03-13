from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.comment import NormalizedComment
from app.models.enums import SignalStatus
from app.repositories.classifications import ClassificationRepository
from app.repositories.signals import SignalRepository
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.signals import SignalCommentEvidence, SignalDetail, SignalExportResponse, SignalRead, SignalUpdate
from app.services.aggregation import SignalAggregationService
from app.services.exports import ExportService

router = APIRouter(prefix="/signals")


@router.get("", response_model=PaginatedResponse[SignalRead])
def list_signals(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(db_session),
) -> PaginatedResponse[SignalRead]:
    items, total = SignalRepository(session).list(limit=limit, offset=offset)
    return PaginatedResponse[SignalRead](
        items=[SignalRead.model_validate(item) for item in items],
        meta=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{signal_id}", response_model=SignalDetail)
def get_signal(signal_id: UUID, session: Session = Depends(db_session)) -> SignalDetail:
    repository = SignalRepository(session)
    signal = repository.get(signal_id)
    if not signal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found.")

    linked_comments: list[SignalCommentEvidence] = []
    for link in repository.get_links(signal_id):
        comment = session.get(NormalizedComment, link.normalized_comment_id)
        if not comment:
            continue
        linked_comments.append(
            SignalCommentEvidence(
                normalized_comment_id=comment.id,
                classification_id=link.classification_id,
                comment_text=comment.original_text,
                author_handle=comment.author_handle,
                relevance_score=link.relevance_score,
            )
        )

    return SignalDetail.model_validate({**SignalRead.model_validate(signal).model_dump(), "linked_comments": linked_comments})


@router.post("/rebuild", response_model=MessageResponse)
def rebuild_signals(session: Session = Depends(db_session)) -> MessageResponse:
    repository = SignalRepository(session)
    signals, links = SignalAggregationService(ClassificationRepository(session)).rebuild(
        existing_signals=repository.existing_by_fingerprint()
    )
    repository.replace_all(signals=signals, links=links)
    session.commit()
    return MessageResponse(message=f"Rebuilt {len(signals)} signals.")


@router.patch("/{signal_id}", response_model=SignalRead)
def update_signal(
    signal_id: UUID,
    payload: SignalUpdate,
    session: Session = Depends(db_session),
) -> SignalRead:
    repository = SignalRepository(session)
    signal = repository.get(signal_id)
    if not signal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found.")

    values = payload.model_dump(exclude_none=True)
    if payload.status == SignalStatus.REVIEWED:
        values["reviewed_at"] = datetime.now(UTC)
    updated = repository.update(signal, values)
    session.commit()
    session.refresh(updated)
    return SignalRead.model_validate(updated)


@router.post("/{signal_id}/export/github", response_model=SignalExportResponse)
def export_signal_github(signal_id: UUID, session: Session = Depends(db_session)) -> SignalExportResponse:
    repository = SignalRepository(session)
    signal = repository.get(signal_id)
    if not signal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found.")

    response = ExportService().export_to_github(signal)
    metadata = dict(signal.export_metadata)
    metadata["github"] = response.model_dump(mode="json")
    repository.update(signal, {"export_metadata": metadata})
    session.commit()
    return response


@router.post("/{signal_id}/export/trello", response_model=SignalExportResponse)
def export_signal_trello(signal_id: UUID, session: Session = Depends(db_session)) -> SignalExportResponse:
    repository = SignalRepository(session)
    signal = repository.get(signal_id)
    if not signal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found.")

    response = ExportService().export_to_trello(signal)
    metadata = dict(signal.export_metadata)
    metadata["trello"] = response.model_dump(mode="json")
    repository.update(signal, {"export_metadata": metadata})
    session.commit()
    return response
