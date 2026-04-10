"""Sensor platform for Weishaupt Heat Pump."""

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
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import WeishauptData

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity


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
    # Total energy
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
    # Heating energy
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
    # Hot water energy
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
    # Electric energy consumed
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
    # Cooling energy
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

ALL_SENSORS = TEMPERATURE_SENSORS + MISC_SENSORS + ENERGY_SENSORS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeishauptSensor(coordinator, description) for description in ALL_SENSORS
    )


class WeishauptSensor(WeishauptEntity, SensorEntity):
    """A Weishaupt sensor entity."""

    entity_description: WeishauptSensorDescription

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
