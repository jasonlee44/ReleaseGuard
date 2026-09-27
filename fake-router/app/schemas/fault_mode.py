"""Pydantic schemas for fault mode administration.

Will define models for POST /admin/fault-mode request and response,
including mode enum values (normal, slow, error_prone, down, config_bug)
and optional tuning options like delay_ms and error_rate.
"""

from enum import Enum
from pydantic import BaseModel

class FaultMode(str, Enum):
    normal = "normal"
    slow = "slow"
    error_prone = "error_prone"
    down = "down"
    config_bug = "config_bug"

class FaultModeRequest(BaseModel):
    mode: FaultMode
    delay_ms: int = 2000
    error_rate: float = 0.3


class FaultModeResponse(BaseModel):
    mode: FaultMode
    delay_ms: int
    error_rate: float
    message: str
