"""Seeded in-memory device inventory and default configuration.
"""

import copy
from datetime import datetime, timezone

PRODUCT_NAME = "ReleaseGuard Fake Router"
DEFAULT_FIRMWARE_VERSION = "2.4.1"
DEFAULT_BUILD_ID = "router-api-v1.0"

INITIAL_DEVICES: dict[str, dict] = {
    "router-001": {
        "device_id": "router-001",
        "device_type": "edge-router",
        "online": True,
        "cpu_percent": 24.5,
        "memory_percent": 44.0,
        "last_seen": datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc),
        "config_version": 1,
        "config": {
            "hostname": "edge-01",
            "vlan_ids": [10, 20],
            "routing_enabled": True,
        },
    },
    "router-002": {
        "device_id": "router-002",
        "device_type": "core-router",
        "online": True,
        "cpu_percent": 17.0,
        "memory_percent": 35.0,
        "last_seen": datetime(2026, 6, 20, 8, 20, 0, tzinfo=timezone.utc),
        "config_version": 1,
        "config": {
            "hostname": "core-01",
            "vlan_ids": [30, 40],
            "routing_enabled": True,
        },
    },
    "switch-001": {
        "device_id": "switch-001",
        "device_type": "switch",
        "online": False,
        "cpu_percent": 7.0,
        "memory_percent": 15.0,
        "last_seen": datetime(2026, 6, 15, 16, 30, 0, tzinfo=timezone.utc),
        "config_version": 1,
        "config": {
            "hostname": "switch-01",
            "vlan_ids": [50, 60],
            "routing_enabled": False,
        }
    },
}

SEEDED_DEVICES: dict[str, dict] = copy.deepcopy(INITIAL_DEVICES)


def get_device(device_id: str) -> dict | None:
    """Return one device from the live store, or None if missing."""
    return SEEDED_DEVICES.get(device_id)


def list_devices() -> list[dict]:
    """Return all devices in the live store."""
    return list(SEEDED_DEVICES.values())


def update_device_config(device_id: str, new_config: dict) -> dict | None:
    """Replace a device's config, increment config_version, and return a deep copy."""
    device = SEEDED_DEVICES.get(device_id)

    if device is None:
        return None

    device["config"] = copy.deepcopy(new_config)
    device["config_version"] += 1

    return copy.deepcopy(device)


def reset_devices() -> None:
    """Restore SEEDED_DEVICES from INITIAL_DEVICES."""
    SEEDED_DEVICES.clear()
    SEEDED_DEVICES.update(copy.deepcopy(INITIAL_DEVICES))
