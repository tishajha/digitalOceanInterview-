from __future__ import annotations

import queue
import threading
import time
from typing import Any

from app.models import Job, JobStatus
from app.store import InMemoryJobStore


class BackgroundWorkerPool:
    def __init__(self, store: InMemoryJobStore, worker_count: int = 2) -> None:
        self.store = store
        self.worker_count = worker_count
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        for _ in range(self.worker_count):
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()
            self._threads.append(thread)

    def stop(self) -> None:
        self._stop_event.set()
        for _ in self._threads:
            self._queue.put("__stop__")
        for thread in self._threads:
            thread.join(timeout=1)

    def submit(self, job_id: str) -> None:
        self._queue.put(job_id)

    def process_job(self, job_id: str) -> None:
        job = self.store.get_job(job_id)
        if not job:
            return

        for attempt in range(1, 3):
            self.store.increment_attempts(job_id)
            self.store.update_status(job_id, JobStatus.running)
            time.sleep(2)

            if job.payload.get("transient_error"):
                if attempt < 2:
                    self.store.update_status(job_id, JobStatus.queued)
                    continue
                self.store.update_status(job_id, JobStatus.failed, error="Transient error after retries")
                return

            if job.payload.get("fail"):
                self.store.update_status(job_id, JobStatus.failed, error="Processing failed")
                return

            result = {"message": "Processed successfully", "payload": job.payload}
            self.store.update_status(job_id, JobStatus.completed, result=result)
            return

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                job_id = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if job_id == "__stop__":
                self._queue.task_done()
                break

            self.process_job(job_id)
            self._queue.task_done()
