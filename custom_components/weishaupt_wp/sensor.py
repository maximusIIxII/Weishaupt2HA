"""Sensor platform for Weishaupt Heat Pump / Gas Boiler."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import EbusdData, WCMData, WeishauptData

from .const import CONF_CONNECTION_TYPE, ConnectionType
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WCMDataUpdateCoordinator,
    WeishauptConfigEntry,
)
from .entity import EbusdEntity, WCMEntity, WeishauptEntity


# ══════════════════════════════════════════════════════════
#  Modbus TCP sensors (heat pumps)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class WeishauptSensorDescription(SensorEntityDescription):
    """Describes a Weishaupt sensor entity."""

    value_fn: Callable[[WeishauptData], float | int | str | None]


# ── Temperature sensors ──
TEMPERATURE_SENSORS: tuple[WeishauptSensorDescription, ...] = (
    WeishauptSensorDescription(
        key="outdoor_temp",
        translation_key="outdoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.system.outdoor_temp,
    ),
    WeishauptSensorDescription(
        key="air_intake_temp",
        translation_key="air_intake_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.system.air_intake_temp,
    ),
    WeishauptSensorDescription(
        key="hp_flow_temp",
        translation_key="hp_flow_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.flow_temp,
    ),
    WeishauptSensorDescription(
        key="hp_return_temp",
        translation_key="hp_return_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.return_temp,
    ),
    WeishauptSensorDescription(
        key="hp_evaporator_temp",
        translation_key="hp_evaporator_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.evaporator_temp,
    ),
    WeishauptSensorDescription(
        key="hp_compressor_intake_temp",
        translation_key="hp_compressor_intake_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.compressor_intake_temp,
    ),
    WeishauptSensorDescription(
        key="hp_switch_temp",
        translation_key="hp_switch_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.switch_temp,
    ),
    WeishauptSensorDescription(
        key="hp_precise_flow_temp",
        translation_key="hp_precise_flow_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.precise_flow_temp,
    ),
    WeishauptSensorDescription(
        key="hp_buffer_temp",
        translation_key="hp_buffer_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.buffer_temp,
    ),
    WeishauptSensorDescription(
        key="ww_current_temp",
        translation_key="ww_current_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.hot_water.current_temp,
    ),
    WeishauptSensorDescription(
        key="ww_target_temp",
        translation_key="ww_target_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.hot_water.target_temp,
    ),
    WeishauptSensorDescription(
        key="hz_room_temp",
        translation_key="hz_room_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heating_circuit.room_temp,
    ),
    WeishauptSensorDescription(
        key="hz_room_target_temp",
        translation_key="hz_room_target_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heating_circuit.room_target_temp,
    ),
    WeishauptSensorDescription(
        key="hz_flow_temp",
        translation_key="hz_flow_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heating_circuit.flow_temp,
    ),
    WeishauptSensorDescription(
        key="hz_flow_target_temp",
        translation_key="hz_flow_target_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heating_circuit.flow_target_temp,
    ),
)

# ── Percentage / misc sensors ──
MISC_SENSORS: tuple[WeishauptSensorDescription, ...] = (
    WeishauptSensorDescription(
        key="hp_power_request",
        translation_key="hp_power_request",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heat_pump.power_request,
    ),
    WeishauptSensorDescription(
        key="hz_room_humidity",
        translation_key="hz_room_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.heating_circuit.room_humidity,
    ),
    WeishauptSensorDescription(
        key="w2_eheater1_hours",
        translation_key="w2_eheater1_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.secondary_heater.eheater1_hours,
    ),
    WeishauptSensorDescription(
        key="w2_eheater2_hours",
        translation_key="w2_eheater2_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.secondary_heater.eheater2_hours,
    ),
    WeishauptSensorDescription(
        key="w2_eheater1_cycles",
        translation_key="w2_eheater1_cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.secondary_heater.eheater1_cycles,
    ),
    WeishauptSensorDescription(
        key="w2_eheater2_cycles",
        translation_key="w2_eheater2_cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.secondary_heater.eheater2_cycles,
    ),
)

# ── Energy statistics sensors ──
ENERGY_SENSORS: tuple[WeishauptSensorDescription, ...] = (
    WeishauptSensorDescription(
        key="st_total_energy_today",
        translation_key="st_total_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.total.today,
    ),
    WeishauptSensorDescription(
        key="st_total_energy_year",
        translation_key="st_total_energy_year",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.total.year,
    ),
    WeishauptSensorDescription(
        key="st_heating_energy_today",
        translation_key="st_heating_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.heating.today,
    ),
    WeishauptSensorDescription(
        key="st_heating_energy_year",
        translation_key="st_heating_energy_year",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.heating.year,
    ),
    WeishauptSensorDescription(
        key="st_hot_water_energy_today",
        translation_key="st_hot_water_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.hot_water.today,
    ),
    WeishauptSensorDescription(
        key="st_hot_water_energy_year",
        translation_key="st_hot_water_energy_year",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.hot_water.year,
    ),
    WeishauptSensorDescription(
        key="st_electric_energy_today",
        translation_key="st_electric_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.electric.today,
    ),
    WeishauptSensorDescription(
        key="st_electric_energy_year",
        translation_key="st_electric_energy_year",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.electric.year,
    ),
    WeishauptSensorDescription(
        key="st_cooling_energy_today",
        translation_key="st_cooling_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.cooling.today,
    ),
    WeishauptSensorDescription(
        key="st_cooling_energy_year",
        translation_key="st_cooling_energy_year",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: d.statistics.cooling.year,
    ),
)

ALL_MODBUS_SENSORS = TEMPERATURE_SENSORS + MISC_SENSORS + ENERGY_SENSORS


# ══════════════════════════════════════════════════════════
#  WCM-COM HTTP sensors (gas boilers / WTC)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class WCMSensorDescription(SensorEntityDescription):
    """Describes a WCM-COM sensor entity."""

    value_fn: Callable[[WCMData], float | int | str | None]


WCM_TEMPERATURE_SENSORS: tuple[WCMSensorDescription, ...] = (
    WCMSensorDescription(
        key="wcm_outdoor_temp",
        translation_key="wcm_outdoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.outdoor_temp,
    ),
    WCMSensorDescription(
        key="wcm_damped_outdoor_temp",
        translation_key="wcm_damped_outdoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.damped_outdoor_temp,
    ),
    WCMSensorDescription(
        key="wcm_flow_temp",
        translation_key="wcm_flow_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.flow_temp,
    ),
    WCMSensorDescription(
        key="wcm_return_temp",
        translation_key="wcm_return_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.return_temp,
    ),
    WCMSensorDescription(
        key="wcm_hot_water_temp",
        translation_key="wcm_hot_water_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.hot_water_temp,
    ),
    WCMSensorDescription(
        key="wcm_exhaust_temp",
        translation_key="wcm_exhaust_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.exhaust_temp,
    ),
    WCMSensorDescription(
        key="wcm_buffer_top_temp",
        translation_key="wcm_buffer_top_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.buffer_top_temp,
    ),
    WCMSensorDescription(
        key="wcm_buffer_bottom_temp",
        translation_key="wcm_buffer_bottom_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.buffer_bottom_temp,
    ),
    WCMSensorDescription(
        key="wcm_heat_request",
        translation_key="wcm_heat_request",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.heat_request,
    ),
)

WCM_OPERATIONAL_SENSORS: tuple[WCMSensorDescription, ...] = (
    WCMSensorDescription(
        key="wcm_load_position",
        translation_key="wcm_load_position",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
        value_fn=lambda d: d.sensors.load_position,
    ),
    WCMSensorDescription(
        key="wcm_load_setting_kw",
        translation_key="wcm_load_setting_kw",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.load_setting_kw,
    ),
    WCMSensorDescription(
        key="wcm_flow_rate",
        translation_key="wcm_flow_rate",
        native_unit_of_measurement="l/min",
        icon="mdi:water-pump",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.flow_rate,
    ),
    WCMSensorDescription(
        key="wcm_operating_phase",
        translation_key="wcm_operating_phase",
        icon="mdi:state-machine",
        value_fn=lambda d: _operating_phase_name(d.sensors.operating_phase),
    ),
    WCMSensorDescription(
        key="wcm_error_code",
        translation_key="wcm_error_code",
        icon="mdi:alert-circle-outline",
        value_fn=lambda d: d.sensors.error_code,
    ),
)

WCM_STATISTICS_SENSORS: tuple[WCMSensorDescription, ...] = (
    WCMSensorDescription(
        key="wcm_burner_hours",
        translation_key="wcm_burner_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
        value_fn=lambda d: d.statistics.burner_hours,
    ),
    WCMSensorDescription(
        key="wcm_burner_cycles",
        translation_key="wcm_burner_cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda d: d.statistics.burner_cycles,
    ),
)

ALL_WCM_SENSORS = WCM_TEMPERATURE_SENSORS + WCM_OPERATIONAL_SENSORS + WCM_STATISTICS_SENSORS


# ══════════════════════════════════════════════════════════
#  ebusd sensors (gas boilers via eBUS Adapter)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class EbusdSensorDescription(SensorEntityDescription):
    """Describes an ebusd sensor entity."""

    value_fn: Callable[[EbusdData], float | int | str | None]


EBUSD_TEMPERATURE_SENSORS: tuple[EbusdSensorDescription, ...] = (
    EbusdSensorDescription(
        key="ebusd_outdoor_temp",
        translation_key="ebusd_outdoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.outdoor_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_flow_temp",
        translation_key="ebusd_flow_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.flow_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_flow_set_temp",
        translation_key="ebusd_flow_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.flow_set_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_hot_water_temp",
        translation_key="ebusd_hot_water_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.hot_water_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_dhw_set_temp",
        translation_key="ebusd_dhw_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.dhw_set_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_exhaust_temp",
        translation_key="ebusd_exhaust_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.exhaust_temp,
    ),
    EbusdSensorDescription(
        key="ebusd_trend_temp",
        translation_key="ebusd_trend_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.sensors.trend_temp,
    ),
)

EBUSD_OPERATIONAL_SENSORS: tuple[EbusdSensorDescription, ...] = (
    EbusdSensorDescription(
        key="ebusd_load_position",
        translation_key="ebusd_load_position",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
        value_fn=lambda d: d.sensors.load_position,
    ),
    EbusdSensorDescription(
        key="ebusd_operating_phase",
        translation_key="ebusd_operating_phase",
        icon="mdi:state-machine",
        value_fn=lambda d: d.sensors.operating_phase,
    ),
    EbusdSensorDescription(
        key="ebusd_operating_mode",
        translation_key="ebusd_operating_mode",
        icon="mdi:sun-snowflake-variant",
        value_fn=lambda d: d.sensors.operating_mode,
    ),
    EbusdSensorDescription(
        key="ebusd_season",
        translation_key="ebusd_season",
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda d: d.sensors.season,
    ),
    EbusdSensorDescription(
        key="ebusd_hc_status",
        translation_key="ebusd_hc_status",
        icon="mdi:radiator",
        value_fn=lambda d: d.sensors.hc_status,
    ),
)

ALL_EBUSD_SENSORS = EBUSD_TEMPERATURE_SENSORS + EBUSD_OPERATIONAL_SENSORS


def _operating_phase_name(phase: int | None) -> str | None:
    """Convert operating phase number to name."""
    if phase is None:
        return None
    phases = {
        0: "Standby",
        1: "Heizen",
        2: "Warmwasser",
    }
    return phases.get(phase, f"Unbekannt ({phase})")


# ══════════════════════════════════════════════════════════
#  Platform setup
# ══════════════════════════════════════════════════════════

async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt sensor entities."""
    conn_type = entry.data.get(CONF_CONNECTION_TYPE, ConnectionType.MODBUS_TCP)

    if conn_type == ConnectionType.WCM_HTTP:
        coordinator = entry.runtime_data
        assert isinstance(coordinator, WCMDataUpdateCoordinator)
        async_add_entities(
            WCMSensor(coordinator, description)
            for description in ALL_WCM_SENSORS
        )
    elif conn_type == ConnectionType.EBUSD:
        coordinator = entry.runtime_data
        assert isinstance(coordinator, EbusdDataUpdateCoordinator)
        async_add_entities(
            EbusdSensor(coordinator, description)
            for description in ALL_EBUSD_SENSORS
        )
    else:
        coordinator = entry.runtime_data
        async_add_entities(
            WeishauptSensor(coordinator, description)
            for description in ALL_MODBUS_SENSORS
        )


class WeishauptSensor(WeishauptEntity, SensorEntity):
    """A Weishaupt heat pump sensor entity (Modbus)."""

    entity_description: WeishauptSensorDescription

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)


class WCMSensor(WCMEntity, SensorEntity):
    """A WCM-COM gas boiler sensor entity (HTTP)."""

    entity_description: WCMSensorDescription

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)


class EbusdSensor(EbusdEntity, SensorEntity):
    """An ebusd gas boiler sensor entity (eBUS Adapter)."""

    entity_description: EbusdSensorDescription

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
