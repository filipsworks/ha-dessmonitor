"""Utility functions for DessMonitor integration."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


def create_device_info(
    device_sn: str,
    device_meta: dict[str, Any],
    collector_meta: dict[str, Any],
) -> DeviceInfo:
    """Create device info dictionary for a DessMonitor device.

    Args:
        device_sn: The device serial number
        device_meta: Device metadata from API
        collector_meta: Collector metadata from API

    Returns:
        DeviceInfo dictionary for Home Assistant
    """
    collector_pn = collector_meta.get("pn", "Unknown")
    device_alias = device_meta.get("alias")
    firmware = device_meta.get("firmware") or collector_meta.get("fireware", "Unknown")
    is_local = device_meta.get("connection_type") == "local"

    if not device_alias:
        device_name = f"Inverter {collector_pn}"
    else:
        device_name = f"{device_alias} ({collector_pn})"

    return DeviceInfo(
        identifiers={(DOMAIN, device_sn)},
        name=device_name,
        manufacturer="Local inverter" if is_local else "DessMonitor",
        model=device_meta.get("model", "Energy Storage Inverter"),
        sw_version=firmware,
        serial_number=device_sn,
    )


# Control fields carrying a clock value are reported by the API exactly like a
# numeric setting: no unit and no options. They are told apart by the shape of
# the value itself rather than by a list of field ids, so a firmware that adds
# another timer is picked up without a code change.
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
_DATETIME_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})[ T]([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"
)

TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def control_value_kind(value: Any) -> str | None:
    """Classify a unitless control value as ``"time"``, ``"datetime"``, or None.

    ``None`` means the value is not a clock value and belongs to the numeric
    ``number`` platform.
    """
    if not isinstance(value, str):
        return None

    text = value.strip()
    if _TIME_RE.match(text):
        return "time"
    if _DATETIME_RE.match(text):
        return "datetime"
    return None
