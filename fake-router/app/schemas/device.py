"""Pydantic schemas for device inventory and status endpoints.

Will define models for device list items, device status payloads, and
related request/response bodies for GET /devices and GET /devices/{id}/status.
"""
from datetime import datetime
from pydantic import BaseModel, Field

class DeviceSummary(BaseModel):
    device_id: str
    device_type: str = Field(alias="type")
    online: bool

class DeviceListData(BaseModel):
    devices: list[DeviceSummary]
    count: int

class DeviceStatusData(BaseModel):
    device_id: str
    online: bool
    cpu_percent: float
    memory_percent: float
    last_seen: datetime