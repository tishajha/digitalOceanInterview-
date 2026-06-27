from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from queue import Queue
from threading import Thread, Lock
from uuid import uuid4
import time

app = FastAPI()

job_queue = Queue()
jobs = {}
lock = Lock()

class JobRequest(BaseModel):
    payload: dict

def worker():
    while True:
        job_id = job_queue.get()

        with lock:
            jobs[job_id]["status"] = "running"

        try:
            time.sleep(5)

            with lock:
                jobs[job_id]["status"] = "completed"
                jobs[job_id]["result"] = {
                    "message": "Job processed successfully",
                    "payload": jobs[job_id]["payload"]
                }

        except Exception as e:
            with lock:
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = str(e)

        finally:
            job_queue.task_done()

Thread(target=worker, daemon=True).start()

@app.get("/")
def root():
    return {"message": "Async Job API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs")
def create_job(request: JobRequest):
    job_id = str(uuid4())

    with lock:
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "payload": request.payload,
            "result": None
        }

    job_queue.put(job_id)

    return {
        "job_id": job_id,
        "status": "queued"
    }

@app.get("/jobs")
def list_jobs():
    with lock:
        return list(jobs.values())

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    with lock:
        if job_id not in jobs:
            raise HTTPException(status_code=404, detail=f"job not found: {job_id}")
        return jobs[job_id]
