"""Service logic for fault mode management and request-level fault injection.

Will implement setting/reading fault mode, applying delays, random errors,
down responses, and config_bug behavior before or during handler execution.
"""
from app.fault import state
from app.schemas.fault_mode import FaultMode, FaultModeResponse 

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