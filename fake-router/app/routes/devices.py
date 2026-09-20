"""Routes for simulated network device operations.

Planned endpoints:
    GET  /devices                      — list all seeded devices
    GET  /devices/{device_id}/status   — read operational status for one device
    GET  /devices/{device_id}/config   — read running configuration
    POST /devices/{device_id}/config   — apply a configuration update
"""
from fastapi import APIRouter, HTTPException
from app.services import device_service
from app.schemas.device import DeviceListData, DeviceStatusData
from app.schemas.config import DeviceConfigData, DeviceConfigUpdateData, DeviceConfigUpdateRequest

router = APIRouter()

@router.get("/devices")
async def get_devices() -> DeviceListData:
    return device_service.get_device_list()

@router.get("/devices/{device_id}/status")
async def get_device_status(device_id: str) -> DeviceStatusData:
    response = device_service.get_device_status(device_id)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
            )
    return response

@router.get("/devices/{device_id}/config")
async def get_device_config(device_id: str) -> DeviceConfigData:
    response = device_service.get_device_config(device_id)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
        )
    return response

@router.post("/devices/{device_id}/config")
async def set_device_config(device_id: str, new_config: DeviceConfigUpdateRequest) -> DeviceConfigUpdateData:
    response = device_service.update_device_config(device_id, new_config.config)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device with id {device_id} not found."
        )
    return response