"""Routes for service health and liveness checks.

GET /health — returns service status for liveness probes; subject to fault injection.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import fault_service

router = APIRouter()

class HealthCheck(BaseModel):
    status: str = "OK"

@router.get("/health")
async def health_check() -> HealthCheck:
    await fault_service.apply_faults()
    return HealthCheck(status="OK")
