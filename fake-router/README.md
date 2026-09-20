# ReleaseGuard — Phase 1: Fake Router Service

Simulated router/network device API for ReleaseGuard release reliability testing.

Phase 1 scaffolds the service structure only. Endpoint logic, schemas, fault
injection, and tests will be added in later steps.

## Planned endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness / service status |
| GET | `/devices` | List seeded devices |
| GET | `/devices/{device_id}/status` | Device operational status |
| GET | `/devices/{device_id}/config` | Read running config |
| POST | `/devices/{device_id}/config` | Apply config update |
| GET | `/firmware/version` | Firmware and build info |
| POST | `/admin/fault-mode` | Set fault mode for testing |

## Planned fault modes

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

## Setup (once implementation begins)

From the `fake-router/` directory:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Interactive API docs will be at `http://localhost:8001/docs`.

## Next steps

1. Implement Pydantic schemas in `app/schemas/`
2. Add seeded device data in `app/data/seed.py`
3. Implement fault mode state in `app/fault/state.py`
4. Build service functions in `app/services/`
5. Wire routes in `app/routes/` and register them in `app/main.py`
6. Add pytest coverage in `tests/`
