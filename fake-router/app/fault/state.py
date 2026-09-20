"""Global fault mode state for the Fake Router Service.

Will track the active fault mode (normal, slow, error_prone, down,
config_bug), optional tuning parameters (delay_ms, error_rate), and
when the mode was last changed. Updated via POST /admin/fault-mode.
"""
from app.schemas.fault_mode import FaultMode

DEFAULT_DELAY_MS = 2000
DEFAULT_ERROR_RATE = 0.3

_fault_state = {
    "mode": FaultMode.normal,
    "delay_ms": DEFAULT_DELAY_MS,
    "error_rate": DEFAULT_ERROR_RATE,
}

def get_fault_state() -> dict:
    return _fault_state.copy()

def set_fault_mode(mode, delay_ms=DEFAULT_DELAY_MS, error_rate=DEFAULT_ERROR_RATE) -> dict:
    _fault_state["mode"] = mode
    _fault_state["delay_ms"] = delay_ms
    _fault_state["error_rate"] = error_rate

    return _fault_state
    
def reset_fault_state() -> None:
    _fault_state["mode"] = FaultMode.normal
    _fault_state["delay_ms"] = DEFAULT_DELAY_MS
    _fault_state["error_rate"] = DEFAULT_ERROR_RATE
