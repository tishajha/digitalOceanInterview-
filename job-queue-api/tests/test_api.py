from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_post_jobs_returns_202_and_job_id():
    response = client.post("/jobs", json={"payload": {"task": "demo"}})
    assert response.status_code == 202
    body = response.json()
    assert "job_id" in body
    assert body["status"] == "queued"


def test_get_job_returns_job_details():
    response = client.post("/jobs", json={"payload": {"task": "demo"}})
    job_id = response.json()["job_id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["job_id"] == job_id
    assert body["status"] in {"queued", "running", "completed", "failed"}


def test_get_invalid_job_returns_404():
    response = client.get("/jobs/not-a-real-job")
    assert response.status_code == 404


def test_post_jobs_with_empty_payload_returns_400():
    response = client.post("/jobs", json={"payload": {}})
    assert response.status_code == 400


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
