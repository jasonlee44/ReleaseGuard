"""Global fault mode state for the Fake Router Service.

Holds mode, delay_ms, error_rate; updated via admin/fault service.
"""

from app.schemas.fault_mode import FaultMode

DEFAULT_DELAY_MS = 2000
DEFAULT_ERROR_RATE = 0.3

_fault_state = {
    "mode": FaultMode.normal,
    "delay_ms": DEFAULT_DELAY_MS,
    "error_rate": DEFAULT_ERROR_RATE
}


def get_fault_state() -> dict:
    """Return a copy of the current fault state."""
    return _fault_state.copy()


def set_fault_mode(
    mode: FaultMode, 
    delay_ms: int = DEFAULT_DELAY_MS, 
    error_rate: float = DEFAULT_ERROR_RATE
) -> dict:
    """Set the current fault state, with optional delay and error values."""
    _fault_state["mode"] = mode
    _fault_state["delay_ms"] = delay_ms
    _fault_state["error_rate"] = error_rate

    return get_fault_state()


def reset_fault_state() -> None:
    """Restore mode and tuning parameters to defaults."""
    _fault_state["mode"] = FaultMode.normal
    _fault_state["delay_ms"] = DEFAULT_DELAY_MS
    _fault_state["error_rate"] = DEFAULT_ERROR_RATE
