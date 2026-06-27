Summary: Build a REST API backed by an asynchronous job queue that accepts work
submissions, processes them in the background, and allows users to check the status of their
jobs.


-----------------------------------------------------------------------------------------------------------
Functional Expectations

  Job Submission: Accept a job payload. Return a job ID immediately; processing must be
  decoupled from the HTTP response.
  Basic Worker Pool: Implement a background worker routine that pulls jobs and
  processes them (e.g., executing a mock function that sleeps to simulate work).
  Status API: Return the current state (queued, running, completed, failed) and result
  payload for any job ID.
  
-----------------------------------------------------------------------------------------------------------

Engineering Expectations

  Architecture Flow Diagram: Include a diagram mapping the HTTP submission through
  the queue and worker execution.
  Concurrency Control: Ensure safe concurrent access to job state updates between the
  HTTP layer and the background workers.
  Testing: Unit tests for the worker logic and integration tests for the API layer.
  CI/CD: A basic GitHub Actions pipeline that runs your tests.
  Documentation: README covering setup, execution, and known limitations.

-----------------------------------------------------------------------------------------------------------


Extensions & Next Steps

  Retry Logic: Add automated retries for jobs that fail due to simulated transient errors.
  Deployment: Deploy the API and worker service to DigitalOcean.
