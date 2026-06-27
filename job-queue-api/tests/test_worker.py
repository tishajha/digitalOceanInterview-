import time

import pytest

from app.service import JobService


def test_submit_job_creates_job_with_queued_status():
    service = JobService(worker_count=1)
    try:
        job = service.submit_job({"task": "demo"})
        assert job.status == "queued"
        assert job.payload == {"task": "demo"}
    finally:
        service.shutdown()


def test_worker_processes_job_and_updates_status_to_completed():
    service = JobService(worker_count=1)
    try:
        job = service.submit_job({"value": 42})

        deadline = time.time() + 5
        current_job = None
        while time.time() < deadline:
            current_job = service.get_job(job.job_id)
            if current_job.status == "completed":
                break
            time.sleep(0.1)

        assert current_job is not None
        assert current_job.status == "completed"
        assert current_job.result is not None
    finally:
        service.shutdown()


def test_failed_job_moves_to_failed_after_retry_limit():
    service = JobService(worker_count=1)
    try:
        job = service.submit_job({"fail": True})

        deadline = time.time() + 5
        current_job = None
        while time.time() < deadline:
            current_job = service.get_job(job.job_id)
            if current_job.status == "failed":
                break
            time.sleep(0.1)

        assert current_job is not None
        assert current_job.status == "failed"
        assert current_job.error is not None
    finally:
        service.shutdown()


def test_get_invalid_job_returns_expected_error():
    service = JobService(worker_count=1)
    try:
        with pytest.raises(ValueError):
            service.get_job("missing-job")
    finally:
        service.shutdown()
