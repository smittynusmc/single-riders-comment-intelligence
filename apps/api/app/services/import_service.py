from __future__ import annotations

from app.adapters.csv_adapter import CsvImportAdapter
from app.models.comment import RawComment
from app.models.enums import IngestionStatus
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository


class ImportService:
    """Persists raw imported comments while keeping adapter concerns isolated."""

    def __init__(self, ingestion_repository: IngestionRunRepository, comment_repository: CommentRepository):
        self.ingestion_repository = ingestion_repository
        self.comment_repository = comment_repository
        self.csv_adapter = CsvImportAdapter()

    def import_csv_bytes(self, *, file_bytes: bytes, filename: str):
        result = self.csv_adapter.import_comments(file_bytes)
        run = self.ingestion_repository.create(
            source_type=result.source_type,
            source_platform=result.source_platform,
            source_label=filename,
            run_metadata={
                "adapter": "csv",
                "source_filename": filename,
                "failed_samples": [failure.model_dump() for failure in result.failures[:10]],
            },
            status=IngestionStatus.PENDING,
        )

        known_ids = self.comment_repository.existing_source_comment_ids(
            source_platform=result.source_platform,
            source_comment_ids=[item.source_comment_id for item in result.comments],
        )
        seen_ids = set(known_ids)
        raw_comments: list[RawComment] = []
        duplicate_rows = 0
        imported_rows = 0

        for item in result.comments:
            is_duplicate = item.source_comment_id in seen_ids
            if is_duplicate:
                duplicate_rows += 1
            else:
                imported_rows += 1
                seen_ids.add(item.source_comment_id)

            raw_comments.append(
                RawComment(
                    ingestion_run_id=run.id,
                    source_platform=item.source_platform,
                    source_video_id=item.source_video_id,
                    source_comment_id=item.source_comment_id,
                    author_handle=item.author_handle,
                    comment_text=item.comment_text,
                    comment_created_at=item.created_at,
                    like_count=item.like_count,
                    reply_count=item.reply_count,
                    row_number=item.row_number,
                    is_duplicate=is_duplicate,
                    payload=item.payload,
                )
            )

        self.comment_repository.create_raw_comments(raw_comments)
        self.ingestion_repository.apply_summary(
            run,
            total_rows=result.total_rows,
            imported_rows=imported_rows,
            duplicate_rows=duplicate_rows,
            failed_rows=len(result.failures),
            status=IngestionStatus.IMPORTED,
        )
        return run
