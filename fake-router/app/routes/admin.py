"""Administrative routes for controlling simulated failure behavior.

Planned endpoints:
    POST /admin/fault-mode — set the active fault mode (normal, slow, error_prone,
                             down, config_bug) and optional tuning parameters
"""

from fastapi import APIRouter
from app.schemas.fault_mode import FaultModeRequest, FaultModeResponse
from app.services import fault_service

router = APIRouter()

@router.post("/admin/fault-mode")
async def set_fault_mode(mode: FaultModeRequest) -> FaultModeResponse:
    return fault_service.set_current_fault_mode(mode.mode)