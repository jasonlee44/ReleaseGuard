"""Service logic for fault mode management and request-level fault injection.

Will implement setting/reading fault mode, applying delays, random errors,
down responses, and config_bug behavior before or during handler execution.
"""
from fastapi import HTTPException
from app.fault import state
from app.schemas.fault_mode import FaultMode, FaultModeResponse
import asyncio
import random

def get_current_fault_mode() -> FaultModeResponse:
    mode = state.get_fault_state()["mode"]
    return FaultModeResponse(
        mode=mode,
        message=f"Current fault mode is {mode.value}"
    )

def set_current_fault_mode(mode: FaultMode) -> FaultModeResponse:
    state.set_fault_mode(mode)
    return FaultModeResponse(
        mode=mode,
        message=f"Fault mode set to {mode.value}"
    )

async def apply_faults() -> None:
    current_state = state.get_fault_state()
    
    if current_state["mode"] == FaultMode.down:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )

    elif current_state["mode"] == FaultMode.error_prone:
        if random.random() < current_state["error_rate"]:
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    elif current_state["mode"] == FaultMode.slow:
        await asyncio.sleep(current_state["delay_ms"] / 1000)