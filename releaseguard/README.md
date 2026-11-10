# ReleaseGuard — Phase 2: Test Runner

Backend that creates builds and runs reliability tests against the fake router service.

**Status:** Phase 2 complete. In-memory storage for now; PostgreSQL comes in Phase 3.

## What it does

1. You create a **build** (a named release, e.g. `router-api` `1.0.0`).
2. You start a **test run** for that build.
3. ReleaseGuard calls the fake router (default `http://localhost:8001`) and runs either the **default** suite (happy path) or the **chaos** suite (reliability probes).
4. It stores structured pass/fail results in memory and returns a summary.

ReleaseGuard runs the tests. The fake router is the thing being tested.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/builds` | Create a build |
| GET | `/builds` | List builds |
| POST | `/test-runs` | Run a suite for a `build_id` (default = happy path) |
| GET | `/test-runs` | List test runs |
| GET | `/test-runs/{run_id}` | Get one test run |

### Create a test run

```json
{ "build_id": "<uuid>" }
```

```json
{ "build_id": "<uuid>", "suite": "chaos" }
```

`suite` is optional and defaults to `"default"`. Allowed values: `"default"`, `"chaos"`.

## Suites

### Default suite (ship gate) — cases 1–6

Runs under normal mode (no fault injection):

1. `health_check`
2. `devices_list`
3. `device_status`
4. `device_config` (read)
5. `config_update` (write)
6. `firmware_version`

A default run is **`passed`** only if all 6 cases pass. Against a healthy stock fake-router, this suite should **pass**.

### Chaos suite (reliability probes) — cases 7–10

ReleaseGuard sets fault mode, probes, then resets (option A: release fails if the product breaks SLOs under the fault):

1. `slow_response` — fails if latency > 500ms under `slow`
2. `error_prone_service` — fails if `/health` is unhealthy under `error_prone`
3. `down_service` — fails if `/health` is unhealthy under `down`
4. `config_regression` — fails if config does not persist under `config_bug`

A chaos run is **`passed`** only if all 4 cases pass. Against stock fake-router, chaos usually **fails** by design.

## Setup

From the `releaseguard/` directory:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

Start fake-router on port **8001** before creating live test runs.

By default ReleaseGuard calls `http://localhost:8001`. Override with:

```bash
export FAKE_ROUTER_URL=http://localhost:8001
```

## Tests

```bash
pytest
```

Optional live check (fake-router must be running):

```bash
RUN_INTEGRATION=1 pytest -m integration
```
