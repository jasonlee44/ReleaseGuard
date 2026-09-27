"""Routes for firmware and product version information.

Planned endpoints:
    GET /firmware/version — returns product name, firmware version, and build id
"""
from fastapi import APIRouter
from app.schemas.firmware import FirmwareVersionData
from app.services import device_service, fault_service

router = APIRouter()

@router.get("/firmware/version")
async def get_firmware() -> FirmwareVersionData:
    await fault_service.apply_faults()
    return device_service.get_firmware_version()