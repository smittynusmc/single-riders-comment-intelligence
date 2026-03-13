from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.signal import MvpSignal, SignalCommentLink


class SignalRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, *, limit: int = 50, offset: int = 0) -> tuple[list[MvpSignal], int]:
        total = self.session.scalar(select(func.count()).select_from(MvpSignal)) or 0
        stmt = select(MvpSignal).order_by(MvpSignal.priority_score.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt)), total

    def get(self, signal_id: UUID) -> MvpSignal | None:
        return self.session.get(MvpSignal, signal_id)

    def get_links(self, signal_id: UUID) -> list[SignalCommentLink]:
        stmt = select(SignalCommentLink).where(SignalCommentLink.signal_id == signal_id)
        return list(self.session.scalars(stmt))

    def existing_by_fingerprint(self) -> dict[str, MvpSignal]:
        stmt = select(MvpSignal)
        return {signal.fingerprint: signal for signal in self.session.scalars(stmt)}

    def replace_all(self, *, signals: list[MvpSignal], links: list[SignalCommentLink]) -> None:
        self.session.execute(delete(SignalCommentLink))
        self.session.execute(delete(MvpSignal))
        self.session.flush()
        self.session.add_all(signals)
        self.session.flush()
        self.session.add_all(links)
        self.session.flush()

    def update(self, signal: MvpSignal, values: dict) -> MvpSignal:
        for key, value in values.items():
            if value is not None:
                setattr(signal, key, value)
        self.session.add(signal)
        self.session.flush()
        return signal

    def top(self, limit: int = 5) -> list[MvpSignal]:
        stmt = select(MvpSignal).order_by(MvpSignal.priority_score.desc()).limit(limit)
        return list(self.session.scalars(stmt))
