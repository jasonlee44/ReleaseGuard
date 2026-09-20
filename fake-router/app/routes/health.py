"""Routes for service health and liveness checks.

Planned endpoints:
    GET /health — returns service status and uptime for liveness probes.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    status: str = "OK"

@router.get("/health")
async def health_check() -> HealthCheck:
    return HealthCheck(status="OK")