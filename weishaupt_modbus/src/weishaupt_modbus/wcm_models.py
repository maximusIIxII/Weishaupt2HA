"""Data models for WCM-COM HTTP API (gas boiler / WTC) data."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WCMDeviceInfo:
    """WCM-COM device identification."""

    device_name: str = "Weishaupt WTC"
    device_type_id: int = 0
    hostname: str = "wcm-com"
    firmware_version: int = 0
    serial_number: str = "unknown"


@dataclass
class WTCSensorData:
    """WTC gas boiler sensor readings."""

    # Temperatures (°C), None = not available
    outdoor_temp: float | None = None
    damped_outdoor_temp: float | None = None
    flow_temp: float | None = None
    return_temp: float | None = None
    hot_water_temp: float | None = None
    exhaust_temp: float | None = None
    buffer_top_temp: float | None = None
    buffer_bottom_temp: float | None = None

    # Operational values
    heat_request: float | None = None       # °C — requested temperature
    load_position: int | None = None        # % — burner modulation
    load_setting_kw: float | None = None    # kW — current power output
    flow_rate: float | None = None          # l/min
    operating_phase: int | None = None      # 0=standby, 1=heating, 2=hot water

    # Status
    error_code: int = 0                     # 0 = no error


@dataclass
class WTCStatisticsData:
    """WTC gas boiler statistics / counters."""

    burner_hours: int = 0
    burner_cycles: int = 0
    burner_stage1_hours: int = 0
    burner_stage1_cycles: int = 0
    oil_meter: float = 0.0                  # Liters (combined high+low)


@dataclass
class WCMData:
    """Complete data snapshot from a WCM-COM module (gas boiler)."""

    sensors: WTCSensorData = field(default_factory=WTCSensorData)
    statistics: WTCStatisticsData = field(default_factory=WTCStatisticsData)
    device_info: WCMDeviceInfo = field(default_factory=WCMDeviceInfo)
    raw_values: dict[int, int | float | str | None] = field(default_factory=dict)
