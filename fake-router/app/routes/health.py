"""Routes for service health and liveness checks.

Planned endpoints:
    GET /health — returns service status and uptime for liveness probes.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.services import fault_service

router = APIRouter()

class HealthCheck(BaseModel):
    status: str = "OK"

@router.get("/health")
async def health_check() -> HealthCheck:
    await fault_service.apply_faults()
    return HealthCheck(status="OK")