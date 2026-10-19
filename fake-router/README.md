# ReleaseGuard - Phase 1: Fake Router Service

Simulated router/network device API used by ReleaseGuard for release reliability testing.

This service is implemented. It behaves normally by default and can be switched into fault modes so later ReleaseGuard tests have realistic failures to catch. Device data is kept in memory (no database).

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness / service status |
| GET | `/devices` | List seeded devices |
| GET | `/devices/{device_id}/status` | Device operational status |
| GET | `/devices/{device_id}/config` | Read running config |
| POST | `/devices/{device_id}/config` | Apply config update |
| GET | `/firmware/version` | Firmware and build info |
| POST | `/admin/fault-mode` | Set fault mode for testing |

## Fault modes

Set a global mode with `POST /admin/fault-mode`. Optional body fields: `delay_ms` (for `slow`) and `error_rate` (for `error_prone`).

- `normal` — healthy behavior
- `slow` — injected latency
- `error_prone` — random server errors
- `down` — service unavailable responses
- `config_bug` — silent config read/write inconsistency

## Project layout

```
fake-router/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/              # HTTP route handlers (by domain)
│   ├── schemas/             # Pydantic request/response models
│   ├── data/                # In-memory seeded device store
│   ├── fault/               # Global fault mode state
│   └── services/            # Business logic layer
├── tests/                   # pytest test suite
├── requirements.txt
└── README.md
```

## Setup

From the `fake-router/` directory:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Interactive API docs: `http://localhost:8001/docs`

## Tests

With the virtualenv activated:

```bash
pytest
```
