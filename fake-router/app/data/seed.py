"""Seeded in-memory device inventory and default configuration.

Will hold fixed starter devices (e.g. router-001, router-002, switch-001)
and their initial config documents. Route handlers and services will read
and mutate this store during normal operation and config_bug fault mode.
"""
from datetime import datetime, timezone
import copy

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
    }
}

SEEDED_DEVICES: dict[str, dict] = copy.deepcopy(INITIAL_DEVICES)

def get_device(device_id) -> dict | None:
    return SEEDED_DEVICES.get(device_id)

def list_devices() -> list[dict]:
    return list(SEEDED_DEVICES.values())

def update_device_config(device_id, new_config) -> dict | None:
    device = SEEDED_DEVICES.get(device_id)

    if device is None:
        return None

    device["config"] = copy.deepcopy(new_config)
    device["config_version"] += 1

    return device

def reset_devices():
    SEEDED_DEVICES.clear()
    SEEDED_DEVICES.update(copy.deepcopy(INITIAL_DEVICES))
