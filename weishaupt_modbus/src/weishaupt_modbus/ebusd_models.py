"""Data models for ebusd communication (eBUS Adapter + Weishaupt WTC).

Field set validated against a Weishaupt WTC 25-A (2026-04-18). Populated
from the sc.Act and hc1.Set broadcast messages — see ebusd_const.py for
the field-index mapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EbusdDeviceInfo:
    """ebusd device identification."""

    ebusd_version: str = "unknown"
    device_name: str = "Weishaupt WTC"
    signal_state: str = "unknown"
    serial_number: str = "unknown"


@dataclass
class EbusdSensorData:
    """WTC live readings extracted from sc.Act and hc1.Set broadcasts."""

    # Temperatures (°C), None = not available
    outdoor_temp: float | None = None
    flow_temp: float | None = None
    flow_set_temp: float | None = None
    hot_water_temp: float | None = None
    dhw_set_temp: float | None = None
    exhaust_temp: float | None = None
    trend_temp: float | None = None

    # Operational values
    load_position: int | None = None
    operating_phase: str | None = None
    season: str | None = None
    operating_mode: str | None = None
    hc_status: str | None = None

    # Binary states (stored as 0/1, converted to bool in entities)
    flame_active: int | None = None
    pump_active: int | None = None
    error_active: int | None = None
    gas_valve1_active: int | None = None
    gas_valve2_active: int | None = None

    # Editable setpoints — read actively, written via async_write_field.
    # Populated only when the ebusd instance has hc.user.inc / hwc.user.inc
    # loaded (i.e. not running with --scanconfig on a flat J0EK3R layout).
    summer_threshold: float | None = None
    room_normal_temp: float | None = None
    room_reduced_temp: float | None = None
    frost_protection_temp: float | None = None
    heating_curve_gradient: float | None = None
    dhw_setpoint: float | None = None
    dhw_min: float | None = None


@dataclass
class EbusdData:
    """Complete data snapshot from ebusd."""

    sensors: EbusdSensorData = field(default_factory=EbusdSensorData)
    device_info: EbusdDeviceInfo = field(default_factory=EbusdDeviceInfo)
    raw_values: dict[str, float | int | str | None] = field(default_factory=dict)
