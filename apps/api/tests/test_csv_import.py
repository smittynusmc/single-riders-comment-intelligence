from __future__ import annotations

from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.services.import_service import ImportService

CSV_CONTENT = b"""source_video_id,source_comment_id,author_handle,comment_text,created_at,like_count,reply_count
video-1,comment-1,userone,Need a meetup feature,2026-03-01T10:00:00Z,10,2
video-1,comment-1,userone,Need a meetup feature,2026-03-01T10:00:00Z,10,2
video-2,comment-2,usertwo,Please add a bot filter,2026-03-01T11:00:00Z,5,1
"""


def test_csv_import_persists_raw_comments_and_duplicates(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    run = service.import_csv_bytes(file_bytes=CSV_CONTENT, filename="comments.csv")
    db_session.commit()

    assert run.total_rows == 3
    assert run.imported_rows == 2
    assert run.duplicate_rows == 1
    assert run.failed_rows == 0

    raw_comments = CommentRepository(db_session).pending_raw_comments_for_run(run.id)
    assert len(raw_comments) == 2
