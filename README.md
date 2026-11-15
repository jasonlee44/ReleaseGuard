# ReleaseGuard

> A tool that checks whether a new software release is safe to ship.

**Stack:** Python · FastAPI · Pydantic · SQLAlchemy · PostgreSQL · Docker Compose · httpx · pytest  
*(planned: GitHub Actions, React/TypeScript)*

ReleaseGuard is a release reliability checker for backend services. You register a build (a named version of a release), and ReleaseGuard runs automated checks against that service to see if it looks safe to ship.

In this project there are two parts:

- **`releaseguard/`** — the test runner. Creates builds, runs checks, stores pass/fail results in PostgreSQL.
- **`fake-router/`** — the service under test. A simulated network/device API that can behave normally or fail on purpose (slow responses, random errors, downtime).

## Quick start

```bash
git clone https://github.com/jasonlee44/ReleaseGuard.git
cd ReleaseGuard
```

### Docker Compose (recommended for local demo)

Requires Docker (e.g. Colima or Docker Desktop) running.

```bash
docker compose up --build
```

Then open:

- ReleaseGuard docs: `http://localhost:8000/docs`
- Fake router docs: `http://localhost:8001/docs`

Smoke path: create a build → start a **default** suite test run → expect **passed** against stock fake-router. Use `"suite": "chaos"` for reliability probes — those often end **`failed`** on purpose.

Ports: **8000** (releaseguard), **8001** (fake-router), **5432** (Postgres). Stop with Ctrl+C or `docker compose down`.

Host `pytest` does **not** require Compose; keep using local Postgres + `releaseguard_test` as documented in [`releaseguard/README.md`](releaseguard/README.md).

### Without Docker (venvs + local Postgres)

From the repo root (after cloning above). Postgres must be running locally with a `releaseguard` database for the runner.

#### Fake router

More detail is in [`fake-router/README.md`](fake-router/README.md).

```bash
cd fake-router
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then open `http://localhost:8001/docs` to try the API.

#### ReleaseGuard test runner

More detail is in [`releaseguard/README.md`](releaseguard/README.md). Postgres must be running locally with a `releaseguard` database. Start the fake router on port **8001** first if you want test runs to hit a live target.

```bash
cd releaseguard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` to create builds and test runs.

## Current status

**Phase 4 complete.** The full local stack (Postgres, fake-router, releaseguard) runs with Docker Compose. Builds, test runs, and case results are saved in PostgreSQL.

**Today**

- Fake router with health, devices, config, firmware, and fault modes
- ReleaseGuard builds and test runs APIs (default + chaos suites)
- PostgreSQL persistence and Docker Compose one-command demo
- Pytest for the runner (mocked fake-router); optional `RUN_INTEGRATION=1`

**Not yet**

- Auto-generated bug reports
- CI or a frontend

## Architecture

You create a build in ReleaseGuard, start a test run with `suite` set to `default` (ship gate) or `chaos` (reliability probes), and ReleaseGuard stores the results in PostgreSQL.

```text
[You / API docs]
        |
        v
[ReleaseGuard test runner]  --->  [Fake router service]
   (Phase 4: Compose)             (Phase 1: complete)
   port 8000                      port 8001
        |
        v
   [PostgreSQL]
   (Compose service: db)
```

## Repository structure

```text
ReleaseGuard/
├── docker-compose.yml        # Phase 4: db + fake-router + releaseguard
├── fake-router/              # Fake router API (Phase 1)
│   ├── Dockerfile
│   └── README.md
├── releaseguard/             # Test runner + Postgres (Phase 3+)
│   ├── Dockerfile
│   └── README.md
└── README.md                 # Overview of the whole project
```

## Why I built it

When you ship a new backend release, things can break in ways normal "happy path" tests miss. I wanted a project that looks for those failures on purpose, and that also lets me practice backend and infrastructure skills: APIs, testing, reliability, databases, Docker, and CI.

I'm building it step by step, starting with the APIs.

## Roadmap

1. **Phase 1: Fake router service** - build a small API that can behave normally or fail on purpose
2. **Phase 2: Test runner backend** - create builds and run tests against the fake router
3. **Phase 3: PostgreSQL storage** - save builds, test runs, and results
4. **Phase 4: Docker Compose** - run everything locally with one command
5. **Phase 5: Bug report generation** - turn failed tests into a readable report
6. **Phase 6: CI/CD** - run tests automatically on push
7. **Phase 7: Frontend dashboard** - simple UI to view builds and results (only after the backend works)

## Tech stack

| Area                | Technology                                                    |
| ------------------- | ------------------------------------------------------------- |
| Backend             | Python, FastAPI, Pydantic, SQLAlchemy                         |
| HTTP client / tests | httpx, pytest                                                 |
| Database            | PostgreSQL                                                    |
| Infra               | Docker Compose (local demo); GitHub Actions (planned)         |
| Frontend (later)    | React, TypeScript                                             |
