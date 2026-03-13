from __future__ import annotations

from app.jobs.queue import build_rq_worker

worker = build_rq_worker()
