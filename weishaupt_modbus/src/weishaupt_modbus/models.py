"""Data models for Weishaupt heat pump data."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DeviceInfo:
    """Device identification info."""

    device_type: str = "Weishaupt WBB"
    firmware_version: str = "unknown"
    serial_number: str = "unknown"


@dataclass
class SystemData:
    """System-level data."""

    outdoor_temp: float | None = None
    air_intake_temp: float | None = None
    error_code: int = 65535  # 65535 = no error
    warning_code: int = 65535
    error_free: int = 0
    display_status: int = 0
    operation_mode: int = 0
    pv_setpoint: float = 0.0


@dataclass
class HeatPumpData:
    """Heat pump operational data."""

    operation_status: int = 0
    error_status: int = 0
    power_request: float = 0.0
    flow_temp: float | None = None
    return_temp: float | None = None
    evaporator_temp: float | None = None
    compressor_intake_temp: float | None = None
    switch_temp: float | None = None
    request_regen_temp: float | None = None
    buffer_temp: float | None = None
    precise_flow_temp: float | None = None
    # Holding register data (read-only)
    config: int = 0
    quiet_mode: int = 0
    pump_start_mode: int = 0
    pump_power_heating: float = 0.0
    pump_power_cooling: float = 0.0
    pump_power_hot_water: float = 0.0
    pump_power_defrost: float = 0.0
    flow_rate_heating: float = 0.0
    flow_rate_cooling: float = 0.0
    flow_rate_hot_water: float = 0.0


@dataclass
class HotWaterData:
    """Hot water data."""

    target_temp: float | None = None
    current_temp: float | None = None
    # Settings
    config: int = 0
    push_active: int = 0
    normal_temp: float = 50.0
    reduced_temp: float = 40.0
    sg_ready_boost: float = 0.0


@dataclass
class HeatingCircuitData:
    """Heating circuit data."""

    room_target_temp: float | None = None
    room_temp: float | None = None
    room_humidity: float | None = None
    flow_target_temp: float | None = None
    flow_temp: float | None = None
    # Settings
    config: int = 0
    request_type: int = 0
    operation_mode: int = 0
    party_pause: int = 0
    comfort_temp: float = 22.0
    normal_temp: float = 20.0
    reduced_temp: float = 16.0
    heating_curve: float = 0.0
    summer_winter_switch: float = 0.0
    const_temp_heating: float = 0.0
    const_temp_reduced: float = 0.0
    const_temp_cooling: float = 0.0


@dataclass
class SecondaryHeaterData:
    """Secondary heater (2. Wärmeerzeuger) data."""

    status: int = 0
    eheater1_cycles: int = 0
    eheater1_hours: int = 0
    eheater1_status: int = 0
    eheater2_status: int = 0
    eheater2_cycles: int = 0
    eheater2_hours: int = 0
    # Settings
    config: int = 0
    ep1_config: int = 0
    ep2_config: int = 0
    limit_temp: float = 0.0
    bivalence_temp: float = 0.0
    bivalence_temp_ww: float = 0.0


@dataclass
class EnergyBlock:
    """Energy statistics for one category (today/yesterday/month/year)."""

    today: float = 0.0
    yesterday: float = 0.0
    month: float = 0.0
    year: float = 0.0


@dataclass
class StatisticsData:
    """Energy and performance statistics."""

    total: EnergyBlock = field(default_factory=EnergyBlock)
    heating: EnergyBlock = field(default_factory=EnergyBlock)
    hot_water: EnergyBlock = field(default_factory=EnergyBlock)
    cooling: EnergyBlock = field(default_factory=EnergyBlock)
    defrost: EnergyBlock = field(default_factory=EnergyBlock)
    total2: EnergyBlock = field(default_factory=EnergyBlock)
    electric: EnergyBlock = field(default_factory=EnergyBlock)


@dataclass
class WeishauptData:
    """Complete data snapshot from a Weishaupt heat pump."""

    system: SystemData = field(default_factory=SystemData)
    heat_pump: HeatPumpData = field(default_factory=HeatPumpData)
    hot_water: HotWaterData = field(default_factory=HotWaterData)
    heating_circuit: HeatingCircuitData = field(default_factory=HeatingCircuitData)
    secondary_heater: SecondaryHeaterData = field(default_factory=SecondaryHeaterData)
    statistics: StatisticsData = field(default_factory=StatisticsData)
    device_info: DeviceInfo = field(default_factory=DeviceInfo)
