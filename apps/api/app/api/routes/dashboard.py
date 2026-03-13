from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.repositories.signals import SignalRepository
from app.schemas.dashboard import DashboardSummary, TopSignalSummary, TrendPoint
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard")


@router.get("/summary", response_model=DashboardSummary)
def get_summary(session: Session = Depends(db_session)) -> DashboardSummary:
    return DashboardService(session, SignalRepository(session)).get_summary()


@router.get("/trends", response_model=list[TrendPoint])
def get_trends(session: Session = Depends(db_session)) -> list[TrendPoint]:
    return DashboardService(session, SignalRepository(session)).get_trends()


@router.get("/top-signals", response_model=list[TopSignalSummary])
def get_top_signals(session: Session = Depends(db_session)) -> list[TopSignalSummary]:
    return DashboardService(session, SignalRepository(session)).get_top_signals()
