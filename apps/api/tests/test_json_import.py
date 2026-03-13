from __future__ import annotations

from app.models.enums import ImportFormat
from app.repositories.comments import CommentRepository
from app.repositories.ingestion_runs import IngestionRunRepository
from app.services.import_service import ImportService

JSON_CONTENT = b"""{
  "comments": [
    {
      "video_id": "video-1",
      "comment_id": "comment-1",
      "user": { "unique_id": "userone" },
      "text": "Need a meetup feature",
      "create_time": "2026-03-01T10:00:00Z",
      "digg_count": 10,
      "reply_comment_total": 2
    },
    {
      "video_id": "video-1",
      "comment_id": "comment-2",
      "user": { "unique_id": "usertwo" },
      "text": "Please add a bot filter",
      "create_time": "2026-03-01T11:00:00Z",
      "digg_count": 5,
      "reply_comment_total": 1
    }
  ]
}"""

PORTABILITY_JSON_CONTENT = b"""{
  "Activity": {
    "Comments": [
      {
        "Date": "2026-03-01T12:00:00Z",
        "Comment": "This would help with same day rides"
      }
    ]
  }
}"""


def test_json_import_persists_raw_comments(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    run = service.import_json_bytes(file_bytes=JSON_CONTENT, filename="comments.json")
    db_session.commit()

    assert run.total_rows == 2
    assert run.imported_rows == 2
    assert run.duplicate_rows == 0
    assert run.failed_rows == 0
    assert run.import_format == ImportFormat.TIKTOK_JSON


def test_json_preview_detects_portability_shape_and_missing_fields(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    preview = service.preview_upload_bytes(file_bytes=PORTABILITY_JSON_CONTENT, filename="portability.json")

    assert preview.detected_format == ImportFormat.PORTABILITY_JSON
    assert preview.detected_shape == "activity.comments"
    assert preview.comment_count == 1
    assert "source_video_id" in preview.missing_fields
    assert preview.sample_comments[0].source_comment_id.startswith("generated-")
