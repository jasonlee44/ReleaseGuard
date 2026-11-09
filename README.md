# ReleaseGuard

> A tool that checks whether a new software release is safe to ship.


ReleaseGuard is a release reliability checker for backend services. You register a build (a named version of a release), and ReleaseGuard runs automated checks against that service to see if it looks safe to ship.

In this project there are two parts:

- **`releaseguard/`** — the test runner. Creates builds, runs checks, stores pass/fail results.
- **`fake-router/`** — the service under test. A simulated network/device API that can behave normally or fail on purpose (slow responses, random errors, downtime).


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

## Current status

Mid Phase 2. The fake router is done, and the test runner can create builds and run a first set of checks against it.

**Today**

- A fake router service (`fake-router/`) that pretends to be a small network/device API
- Endpoints for health, devices, config, firmware, and setting a fault mode
- Ways to make the service act broken (slow, errors, down, etc.) so later tests have something real to catch
- A ReleaseGuard test runner (`releaseguard/`) with in-memory builds and test runs
- Test runs that probe fake-router health, devices, device status/config, and firmware version

**Not yet**

- Saving results in a database
- Docker setup
- Auto-generated bug reports
- CI or a frontend



## Architecture

You create a build in ReleaseGuard, it runs checks against the fake router, and it stores the results in memory for now.

```text
[You / API docs]
        |
        v
[ReleaseGuard test runner]  --->  [Fake router service]
   (Phase 2: in progress)         (Phase 1: implemented)
   port 8000                      port 8001
        |
        v
   [In-memory store]
   (PostgreSQL for Phase 3)
```



## Repository structure

```text
ReleaseGuard/
├── fake-router/              # Fake router API (Phase 1)
│   └── README.md             # How to run this service
├── releaseguard/             # Test runner backend (Phase 2)
│   └── README.md             # How to run the runner
└── README.md                 # Overview of the whole project
```



## Quick start



### Fake router (Phase 1)

More detail is in `[fake-router/README.md](fake-router/README.md)`.

```bash
cd fake-router
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then open `http://localhost:8001/docs` to try the API.

### ReleaseGuard test runner (Phase 2)

More detail is in `[releaseguard/README.md](releaseguard/README.md)`. Start the fake router on port **8001** first if you want test runs to hit a live target.

```bash
cd releaseguard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` to create builds and test runs.


## Tech stack


| Area                | Choices                                       |
| ------------------- | --------------------------------------------- |
| Backend             | Python, FastAPI, Pydantic                     |
| HTTP client / tests | httpx, pytest                                 |
| Database            | PostgreSQL (planned)                          |
| Infra               | Docker / Compose and GitHub Actions (planned) |
| Frontend (later)    | React, TypeScript                             |
