from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status

from app.models import JobRequest
from app.service import JobService

service: JobService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = JobService()
    yield
    if service is not None:
        service.shutdown()


app = FastAPI(title="Job Queue API", lifespan=lifespan)


def get_service() -> JobService:
    global service
    if service is None:
        service = JobService()
    return service


@app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: JobRequest) -> dict[str, Any]:
    try:
        job = get_service().submit_job(payload.payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - simple fallback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unexpected error") from exc

    return {"job_id": job.job_id, "status": job.status}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    try:
        job = get_service().get_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - simple fallback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unexpected error") from exc

    status_value = job.status.value if hasattr(job.status, "value") else job.status
    return {
        "job_id": job.job_id,
        "status": status_value,
        "result": job.result,
        "error": job.error,
        "attempts": job.attempts,
    }


@app.get("/jobs")
def list_jobs() -> list[dict[str, Any]]:
    try:
        jobs = get_service().list_jobs()
    except Exception as exc:  # pragma: no cover - simple fallback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unexpected error") from exc

    return [
        {
            "job_id": job.job_id,
            "status": job.status.value if hasattr(job.status, "value") else job.status,
            "result": job.result,
            "error": job.error,
            "attempts": job.attempts,
        }
        for job in jobs
    ]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
