"""Routes for simulated network device operations.

GET  /devices                      — list all seeded devices
GET  /devices/{device_id}/status   — read operational status for one device
GET  /devices/{device_id}/config   — read running configuration
POST /devices/{device_id}/config   — apply a configuration update
"""

from fastapi import APIRouter, HTTPException

from app.schemas.config import DeviceConfigData, DeviceConfigUpdateData, DeviceConfigUpdateRequest
from app.schemas.device import DeviceListData, DeviceStatusData
from app.services import device_service, fault_service

router = APIRouter()

@router.get("/devices")
async def get_devices() -> DeviceListData:
    await fault_service.apply_faults()
    return device_service.get_device_list()

@router.get("/devices/{device_id}/status")
async def get_device_status(device_id: str) -> DeviceStatusData:
    await fault_service.apply_faults()
    response = device_service.get_device_status(device_id)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
        )
    return response

@router.get("/devices/{device_id}/config")
async def get_device_config(device_id: str) -> DeviceConfigData:
    await fault_service.apply_faults()
    response = device_service.get_device_config(device_id)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
        )
    return response

@router.post("/devices/{device_id}/config")
async def set_device_config(device_id: str, new_config: DeviceConfigUpdateRequest) -> DeviceConfigUpdateData:
    await fault_service.apply_faults()
    response = device_service.update_device_config(device_id, new_config.config)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
        )
    return response
