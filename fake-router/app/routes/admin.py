"""Administrative routes for controlling simulated failure behavior."""

from fastapi import APIRouter

from app.schemas.fault_mode import FaultModeRequest, FaultModeResponse
from app.services import fault_service

router = APIRouter()

@router.post("/admin/fault-mode")
async def set_fault_mode(fault: FaultModeRequest) -> FaultModeResponse:
    """Set the global fault mode and tuning parameters."""
    return fault_service.set_current_fault_mode(fault.mode, fault.delay_ms, fault.error_rate)