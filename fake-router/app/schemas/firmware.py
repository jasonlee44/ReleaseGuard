"""Pydantic schemas for the firmware version endpoint.

Will define models for GET /firmware/version response fields such as
product name, firmware_version, and build_id.
"""
from pydantic import BaseModel

class FirmwareVersionData(BaseModel):
    product: str
    firmware_version: str
    build_id: str