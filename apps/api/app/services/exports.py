from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.models.signal import MvpSignal
from app.schemas.signals import SignalExportResponse

settings = get_settings()


class ExportService:
    """Backlog export layer with safe placeholders for phase 1."""

    def export_to_github(self, signal: MvpSignal) -> SignalExportResponse:
        reference = None
        if settings.github_export_repository:
            reference = f"github://{settings.github_export_repository}/issues/new?title={signal.title}"
        return SignalExportResponse(signal_id=signal.id, destination="github", status="placeholder", reference=reference)

    def export_to_trello(self, signal: MvpSignal) -> SignalExportResponse:
        reference = None
        if settings.trello_board_id:
            reference = f"trello://{settings.trello_board_id}/cards/new?name={signal.title}"
        return SignalExportResponse(signal_id=signal.id, destination="trello", status="placeholder", reference=reference)

    def export_to_docs(self, signal: MvpSignal) -> SignalExportResponse:
        export_dir = Path(settings.docs_export_path)
        export_dir.mkdir(parents=True, exist_ok=True)
        file_path = export_dir / f"signal-{signal.id}.md"
        file_path.write_text(
            f"# {signal.title}\n\n{signal.summary}\n\nPriority: {signal.priority_score}\n",
            encoding="utf-8",
        )
        return SignalExportResponse(signal_id=signal.id, destination="docs", status="written", reference=str(file_path))
