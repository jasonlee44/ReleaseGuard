"""Service logic for fault mode management and request-level fault injection.

This module manages fault mode and applies request level fault injection.
"""

import asyncio
import random

from fastapi import HTTPException

from app.fault import state
from app.schemas.fault_mode import FaultMode, FaultModeResponse


def get_current_fault_mode() -> FaultModeResponse:
    fault = state.get_fault_state()
    
    return FaultModeResponse(
        mode=fault["mode"],
        delay_ms=fault["delay_ms"],
        error_rate=fault["error_rate"],
        message=f"Current fault mode is {fault['mode'].value}"
    )


def set_current_fault_mode(mode: FaultMode, delay_ms: int, error_rate: float) -> FaultModeResponse:
    state.set_fault_mode(mode, delay_ms, error_rate)

    return FaultModeResponse(
        mode=mode,
        delay_ms=delay_ms,
        error_rate=error_rate,
        message=f"Fault mode set to {mode.value}"
    )


async def apply_faults() -> None:
    """Apply the active global fault mode; may raise HTTPException or delay."""
    current_fault = state.get_fault_state()
    
    if current_fault["mode"] == FaultMode.down:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )

    elif current_fault["mode"] == FaultMode.error_prone:
        if random.random() < current_fault["error_rate"]:
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    elif current_fault["mode"] == FaultMode.slow:
        await asyncio.sleep(current_fault["delay_ms"] / 1000)