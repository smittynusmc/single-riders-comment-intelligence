from __future__ import annotations

import hashlib

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

MULTI_MONTH_JSON_CONTENT = b"""{
  "comments": [
    {
      "video_id": "video-1",
      "comment_id": "comment-july",
      "user": { "unique_id": "userone" },
      "text": "Need a meetup feature",
      "create_time": "2025-07-08T11:22:02Z",
      "digg_count": 10,
      "reply_comment_total": 2
    },
    {
      "video_id": "video-2",
      "comment_id": "comment-march",
      "user": { "unique_id": "usertwo" },
      "text": "Please add a bot filter",
      "create_time": "2026-03-07T22:36:43Z",
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

DOWNLOAD_PORTABILITY_JSON_CONTENT = b"""{
  "Comment": {
    "Comments": {
      "App": 1,
      "CommentsList": [
        {
          "date": "2026-03-07 22:36:43",
          "comment": "We are working diligently!",
          "photo": "N/A",
          "url": ""
        }
      ]
    }
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


def test_json_import_records_multi_month_pipeline_audit_metadata(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    run = service.import_json_bytes(file_bytes=MULTI_MONTH_JSON_CONTENT, filename="multi-month-comments.json")
    db_session.commit()

    audit = run.run_metadata["pipeline_audit"]
    assert audit["json_parsing"]["total_comments_seen"] == 2
    assert audit["json_parsing"]["earliest_comment_date"].startswith("2025-07-08")
    assert audit["json_parsing"]["latest_comment_date"].startswith("2026-03-07")
    assert audit["json_parsing"]["months_represented"] == 2
    assert audit["raw_comments_persisted"]["total_comments_seen"] == 2
    assert audit["raw_comments_persisted"]["months_represented"] == 2


def test_json_import_stores_source_artifact_centrally(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    run = service.import_json_bytes(
        file_bytes=JSON_CONTENT,
        filename="comments.json",
        content_type="application/json",
        uploaded_by_email="adam@example.com",
    )
    db_session.commit()

    assert run.uploaded_by_email == "adam@example.com"
    assert run.source_file_content_type == "application/json"
    assert run.source_file_size_bytes == len(JSON_CONTENT)
    assert run.source_file_sha256 == hashlib.sha256(JSON_CONTENT).hexdigest()
    assert run.source_file_blob == JSON_CONTENT
    assert run.run_metadata["source_artifact"]["storage_backend"] == "database_blob"


def test_json_preview_detects_portability_shape_and_missing_fields(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    preview = service.preview_upload_bytes(file_bytes=PORTABILITY_JSON_CONTENT, filename="portability.json")

    assert preview.detected_format == ImportFormat.PORTABILITY_JSON
    assert preview.detected_shape == "activity.comments"
    assert preview.comment_count == 1
    assert str(preview.earliest_comment_date).startswith("2026-03-01")
    assert str(preview.latest_comment_date).startswith("2026-03-01")
    assert preview.months_represented == 1
    assert preview.sections_detected == ["Activity"]
    assert preview.sections_ignored == []
    assert "source_video_id" in preview.missing_fields
    assert preview.sample_comments[0].source_comment_id.startswith("generated-")


def test_json_preview_detects_download_portability_comment_wrapper(db_session):
    service = ImportService(IngestionRunRepository(db_session), CommentRepository(db_session))

    preview = service.preview_upload_bytes(file_bytes=DOWNLOAD_PORTABILITY_JSON_CONTENT, filename="comments.json")

    assert preview.detected_format == ImportFormat.PORTABILITY_JSON
    assert preview.detected_shape == "comment.comments.comments_list"
    assert preview.comment_count == 1
    assert str(preview.earliest_comment_date).startswith("2026-03-07")
    assert str(preview.latest_comment_date).startswith("2026-03-07")
    assert preview.months_represented == 1
    assert preview.sections_detected == ["Comment"]
    assert preview.sections_ignored == []
    assert "source_video_id" in preview.missing_fields
    assert preview.sample_comments[0].source_comment_id.startswith("generated-")
    assert preview.sample_comments[0].comment_text == "We are working diligently!"
