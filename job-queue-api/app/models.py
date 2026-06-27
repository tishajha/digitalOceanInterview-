from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    job_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = JobStatus.queued.value
    result: Any = None
    error: str | None = None
    attempts: int = 0
    created_at: str | None = None
    updated_at: str | None = None
