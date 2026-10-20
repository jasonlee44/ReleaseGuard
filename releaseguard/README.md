# ReleaseGuard — Phase 2: Test Runner

Backend that creates builds and runs reliability tests against the fake router service.

In-memory storage for Phase 2. PostgreSQL comes in Phase 3.

## Setup

From the `releaseguard/` directory:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

The fake router should run separately on port **8001** when you start executing test runs against it.
