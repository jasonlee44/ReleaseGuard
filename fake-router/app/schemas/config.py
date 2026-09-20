"""Pydantic schemas for device configuration read/write endpoints.

Will define models for configuration documents, version numbers, and
request/response bodies for GET and POST /devices/{device_id}/config.
"""
from pydantic import BaseModel

class DeviceConfig(BaseModel):
    hostname: str
    vlan_ids: list[int]
    routing_enabled: bool

class DeviceConfigData(BaseModel):
    device_id: str
    config_version: int
    config: DeviceConfig

class DeviceConfigUpdateRequest(BaseModel):
    config: DeviceConfig

class DeviceConfigUpdateData(BaseModel):
    device_id: str
    config_version: int
    config: DeviceConfig
