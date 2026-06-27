from __future__ import annotations

from typing import Any

from app.models import Job
from app.queue_worker import BackgroundWorkerPool
from app.store import InMemoryJobStore


class JobService:
    def __init__(self, store: InMemoryJobStore | None = None, worker_count: int = 2) -> None:
        self.store = store or InMemoryJobStore()
        self.worker_pool = BackgroundWorkerPool(self.store, worker_count=worker_count)
        self.worker_pool.start()

    def submit_job(self, payload: dict[str, Any]) -> Job:
        if not payload:
            raise ValueError("payload cannot be empty")

        job = self.store.create_job(payload)
        self.worker_pool.submit(job.job_id)
        return job

    def get_job(self, job_id: str | Job) -> Job:
        job_id_value = job_id.job_id if isinstance(job_id, Job) else job_id
        job = self.store.get_job(job_id_value)
        if not job:
            raise ValueError(f"job not found: {job_id_value}")
        return job

    def list_jobs(self) -> list[Job]:
        return self.store.list_jobs()

    def shutdown(self) -> None:
        self.worker_pool.stop()
