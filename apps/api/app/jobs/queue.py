from __future__ import annotations

import os
from typing import Any

from redis import Redis

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

        from rq.queue import Queue

        connection = Redis.from_url(self.settings.redis_url)
        queue = Queue(name=QUEUE_NAME, connection=connection)
        queue.enqueue(process_ingestion_run, run_id)


def build_rq_worker() -> Any:
    if os.name == "nt":
        raise RuntimeError(
            "Direct RQ worker startup is not supported on Windows in this scaffold. "
            "Use SCI_WORKER_MODE=inline locally or run the worker in Docker/Linux."
        )

    from rq import Worker
    from rq.queue import Queue

    connection = Redis.from_url(settings.redis_url)
    queue = Queue(name=QUEUE_NAME, connection=connection)
    return Worker([queue], connection=connection)