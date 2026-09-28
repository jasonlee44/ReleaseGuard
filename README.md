# ReleaseGuard

> A practice project that checks whether a new software release is safe to ship.

When you push a new backend release, things can break in ways that normal "happy path" tests miss: slow responses, random errors, or services going down.

I wanted to build something that looks for those problems on purpose. ReleaseGuard is supposed to run tests against a fake router API, notice when things fail, and eventually write a simple bug report so you know what went wrong.

This is mainly a learning project for backend and infrastructure skills. I'm starting with the APIs and working my way up.

## Current status

Still early. Right now I'm working on Phase 1.

**Today**

- A fake router service (`fake-router/`) that pretends to be a small network/device API
- Endpoints for health, devices, config, firmware, and setting a fault mode
- Ways to make the service act broken (slow, errors, down, etc.) so later tests have something real to catch

**Not yet**

- The main ReleaseGuard test runner (the part that creates builds and runs tests)
- Saving results in a database
- Docker setup
- Auto-generated bug reports
- CI or a frontend



## Architecture

The long-term idea is pretty simple: you create a build, ReleaseGuard runs tests against the fake router, and it stores the results.

Right now only the fake router part exists. The test runner and database are still planned.

```text
[You / API docs]
        |
        v
[ReleaseGuard test runner]  --->  [Fake router service]
   (not built yet)                      (Phase 1: this is what exists)
        |
        v
   [PostgreSQL]
   (not built yet)
```



## Repository structure

```text
ReleaseGuard/
├── fake-router/              # Fake router API (Phase 1)
│   └── README.md             # How to run this service
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

## Roadmap

1. **Phase 1: Fake router service** - build a small API that can behave normally or fail on purpose
2. **Phase 2: Test runner backend** - create builds and run tests against the fake router
3. **Phase 3: PostgreSQL storage** - save builds, test runs, and results
4. **Phase 4: Docker Compose** - run everything locally with one command
5. **Phase 5: Bug report generation** - turn failed tests into a readable report
6. **Phase 6: CI/CD** - run tests automatically on push
7. **Phase 7: Frontend dashboard** - simple UI to view builds and results (only after the backend works)



## Tech stack


| Area                | Choices                                       |
| ------------------- | --------------------------------------------- |
| Backend             | Python, FastAPI, Pydantic                     |
| HTTP client / tests | httpx, pytest                                 |
| Database            | PostgreSQL (planned)                          |
| Infra               | Docker / Compose and GitHub Actions (planned) |
| Frontend (later)    | React, TypeScript                             |


