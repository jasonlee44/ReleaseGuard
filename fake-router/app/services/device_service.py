"""Service logic for device inventory, status, and configuration."""

from app.data import seed
from app.fault import state
from app.schemas.config import DeviceConfig, DeviceConfigData, DeviceConfigUpdateData
from app.schemas.device import DeviceSummary, DeviceListData, DeviceStatusData
from app.schemas.fault_mode import FaultMode
from app.schemas.firmware import FirmwareVersionData


def get_device_list() -> DeviceListData:
    raw_devices = seed.list_devices()
    summaries = []
    for device in raw_devices:
        summaries.append(
            DeviceSummary(
                device_id=device["device_id"],
                type=device["device_type"],
                online=device["online"],
            )
        )
    return DeviceListData(devices=summaries, count=len(summaries))


def get_device_status(device_id: str) -> DeviceStatusData | None:
    device = seed.get_device(device_id)
    if not device:
        return None
    return DeviceStatusData(
        device_id=device_id,
        online=device["online"],
        cpu_percent=device["cpu_percent"],
        memory_percent=device["memory_percent"],
        last_seen=device["last_seen"]
    )


def get_device_config(device_id: str) -> DeviceConfigData | None:
    device = seed.get_device(device_id)
    if not device:
        return None

    return DeviceConfigData(
        device_id=device_id,
        config_version=device["config_version"],
        config=DeviceConfig(
            hostname=device["config"]["hostname"], 
            vlan_ids=device["config"]["vlan_ids"], 
            routing_enabled=device["config"]["routing_enabled"]
            ),
    )


def update_device_config(device_id: str, new_config: DeviceConfig | dict) -> DeviceConfigUpdateData | None:
    """Update the device config from the client's new config. If fault state is config_bug,
    returns success but does not actually update the config.
    """
    if isinstance(new_config, DeviceConfig):
        config_dict = new_config.model_dump()
    else:
        config_dict = new_config

    fault = state.get_fault_state()
    if fault["mode"] == FaultMode.config_bug:
        device = seed.get_device(device_id)
        if not device:
            return None

        return DeviceConfigUpdateData(
            device_id=device_id,
            config_version=device["config_version"] + 1,
            config=DeviceConfig(**config_dict)
        )

    updated = seed.update_device_config(device_id, config_dict)
    if not updated:
        return None

    return DeviceConfigUpdateData(
        device_id=device_id,
        config_version=updated["config_version"],
        config=DeviceConfig(**updated["config"])
    )
    

def get_firmware_version() -> FirmwareVersionData:
    return FirmwareVersionData(
        product=seed.PRODUCT_NAME,
        firmware_version=seed.DEFAULT_FIRMWARE_VERSION,
        build_id=seed.DEFAULT_BUILD_ID
    )
