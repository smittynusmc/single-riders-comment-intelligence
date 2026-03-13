from __future__ import annotations

from redis import Redis
from rq import Queue, Worker

from app.core.config import get_settings
from app.jobs.tasks import process_ingestion_run

settings = get_settings()
QUEUE_NAME = "comment-intelligence"


class TaskQueue:
    def __init__(self):
        self.settings = settings

    def enqueue_ingestion_run(self, run_id: str) -> None:
        if self.settings.worker_mode == "inline":
            process_ingestion_run(run_id)
            return

        connection = Redis.from_url(self.settings.redis_url)
        queue = Queue(name=QUEUE_NAME, connection=connection)
        queue.enqueue(process_ingestion_run, run_id)


def build_rq_worker() -> Worker:
    connection = Redis.from_url(settings.redis_url)
    queue = Queue(name=QUEUE_NAME, connection=connection)
    return Worker([queue], connection=connection)
