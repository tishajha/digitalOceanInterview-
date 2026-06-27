from __future__ import annotations

import uuid
from threading import Lock
from typing import Any

from app.models import Job, JobStatus


class InMemoryJobStore:
    """Simple in-memory job store protected by a lock."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create_job(self, payload: dict[str, Any]) -> Job:
        # The lock prevents HTTP handlers and background workers from
        # mutating the same job dictionary at the same time.
        with self._lock:
            job = Job(
                job_id=str(uuid.uuid4()),
                payload=payload,
                status=JobStatus.queued,
                created_at="",
                updated_at="",
            )
            self._jobs[job.job_id] = job
            return job.model_copy(deep=True)

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.model_copy(deep=True) if job else None

    def update_status(self, job_id: str, status: JobStatus | str, result: Any = None, error: str | None = None) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            updated_job = job.model_copy(deep=True)
            updated_job.status = status.value if isinstance(status, JobStatus) else status
            updated_job.result = result
            updated_job.error = error
            updated_job.updated_at = ""
            self._jobs[job_id] = updated_job
            return updated_job.model_copy(deep=True)

    def increment_attempts(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            updated_job = job.model_copy(deep=True)
            updated_job.attempts += 1
            self._jobs[job_id] = updated_job
            return updated_job.model_copy(deep=True)

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return [job.model_copy(deep=True) for job in self._jobs.values()]
