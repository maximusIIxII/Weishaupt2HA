"""Number platform for Weishaupt Heat Pump — adjustable setpoints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import EbusdData, WeishauptData
from weishaupt_modbus.const import (
    REG_HZ_COMFORT_TEMP,
    REG_HZ_HEATING_CURVE,
    REG_HZ_NORMAL_TEMP,
    REG_HZ_REDUCED_TEMP,
    REG_HZ_SUMMER_WINTER_SWITCH,
    REG_WW_NORMAL_TEMP,
    REG_WW_REDUCED_TEMP,
    REG_W2_BIVALENCE_TEMP,
    REG_W2_LIMIT_TEMP,
    TEMPERATURE_SCALE,
)

from .const import CONF_CONNECTION_TYPE, ConnectionType
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WeishauptConfigEntry,
    WeishauptDataUpdateCoordinator,
)
from .entity import EbusdEntity, WeishauptEntity


@dataclass(frozen=True, kw_only=True)
class WeishauptNumberDescription(NumberEntityDescription):
    """Describes a Weishaupt number entity."""

    value_fn: Callable[[WeishauptData], float | None]
    register_address: int
    scale: float = TEMPERATURE_SCALE


NUMBER_DESCRIPTIONS: tuple[WeishauptNumberDescription, ...] = (
    # Heating circuit temperatures
    WeishauptNumberDescription(
        key="hz_comfort_temp",
        translation_key="hz_comfort_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        value_fn=lambda d: d.heating_circuit.comfort_temp,
        register_address=REG_HZ_COMFORT_TEMP,
    ),
    WeishauptNumberDescription(
        key="hz_normal_temp",
        translation_key="hz_normal_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        value_fn=lambda d: d.heating_circuit.normal_temp,
        register_address=REG_HZ_NORMAL_TEMP,
    ),
    WeishauptNumberDescription(
        key="hz_reduced_temp",
        translation_key="hz_reduced_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=5.0,
        native_max_value=25.0,
        native_step=0.5,
        value_fn=lambda d: d.heating_circuit.reduced_temp,
        register_address=REG_HZ_REDUCED_TEMP,
    ),
    WeishauptNumberDescription(
        key="hz_heating_curve",
        translation_key="hz_heating_curve",
        native_min_value=0.0,
        native_max_value=3.0,
        native_step=0.05,
        mode=NumberMode.BOX,
        value_fn=lambda d: d.heating_circuit.heating_curve,
        register_address=REG_HZ_HEATING_CURVE,
    ),
    WeishauptNumberDescription(
        key="hz_summer_winter_switch",
        translation_key="hz_summer_winter_switch",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        value_fn=lambda d: d.heating_circuit.summer_winter_switch,
        register_address=REG_HZ_SUMMER_WINTER_SWITCH,
    ),
    # Hot water temperatures
    WeishauptNumberDescription(
        key="ww_normal_temp",
        translation_key="ww_normal_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=30.0,
        native_max_value=65.0,
        native_step=0.5,
        value_fn=lambda d: d.hot_water.normal_temp,
        register_address=REG_WW_NORMAL_TEMP,
    ),
    WeishauptNumberDescription(
        key="ww_reduced_temp",
        translation_key="ww_reduced_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=30.0,
        native_max_value=60.0,
        native_step=0.5,
        value_fn=lambda d: d.hot_water.reduced_temp,
        register_address=REG_WW_REDUCED_TEMP,
    ),
    # Secondary heater
    WeishauptNumberDescription(
        key="w2_limit_temp",
        translation_key="w2_limit_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=-20.0,
        native_max_value=10.0,
        native_step=0.5,
        value_fn=lambda d: d.secondary_heater.limit_temp,
        register_address=REG_W2_LIMIT_TEMP,
    ),
    WeishauptNumberDescription(
        key="w2_bivalence_temp",
        translation_key="w2_bivalence_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=-20.0,
        native_max_value=10.0,
        native_step=0.5,
        value_fn=lambda d: d.secondary_heater.bivalence_temp,
        register_address=REG_W2_BIVALENCE_TEMP,
    ),
)


# ══════════════════════════════════════════════════════════
#  ebusd numbers (gas boilers via eBUS Adapter)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class EbusdNumberDescription(NumberEntityDescription):
    """Describes an ebusd number entity."""

    value_fn: Callable[[EbusdData], float | None]
    # The ebusd (circuit, message) pair to write into.
    ebusd_circuit: str
    ebusd_message: str


EBUSD_NUMBERS: tuple[EbusdNumberDescription, ...] = (
    EbusdNumberDescription(
        key="ebusd_summer_threshold",
        translation_key="ebusd_summer_threshold",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=5.0,
        native_max_value=30.0,
        native_step=0.5,
        icon="mdi:sun-snowflake-variant",
        value_fn=lambda d: d.sensors.summer_threshold,
        ebusd_circuit="hc1",
        ebusd_message="SummerWinterChangeOverTemperature",
    ),
    EbusdNumberDescription(
        key="ebusd_room_normal_temp",
        translation_key="ebusd_room_normal_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=25.0,
        native_step=0.5,
        value_fn=lambda d: d.sensors.room_normal_temp,
        ebusd_circuit="hc1",
        ebusd_message="NormalSetTemp",
    ),
    EbusdNumberDescription(
        key="ebusd_room_reduced_temp",
        translation_key="ebusd_room_reduced_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=25.0,
        native_step=0.5,
        value_fn=lambda d: d.sensors.room_reduced_temp,
        ebusd_circuit="hc1",
        ebusd_message="ReducedSetTemp",
    ),
    EbusdNumberDescription(
        key="ebusd_frost_protection",
        translation_key="ebusd_frost_protection",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0.0,
        native_max_value=10.0,
        native_step=0.5,
        icon="mdi:snowflake-thermometer",
        value_fn=lambda d: d.sensors.frost_protection_temp,
        ebusd_circuit="hc1",
        ebusd_message="FrostProtection",
    ),
    EbusdNumberDescription(
        key="ebusd_heating_curve",
        translation_key="ebusd_heating_curve",
        native_min_value=0.0,
        native_max_value=4.0,
        native_step=0.05,
        mode=NumberMode.BOX,
        icon="mdi:chart-bell-curve-cumulative",
        value_fn=lambda d: d.sensors.heating_curve_gradient,
        ebusd_circuit="hc1",
        ebusd_message="Gradient",
    ),
    EbusdNumberDescription(
        key="ebusd_dhw_setpoint",
        translation_key="ebusd_dhw_setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=30.0,
        native_max_value=65.0,
        native_step=0.5,
        icon="mdi:water-thermometer",
        value_fn=lambda d: d.sensors.dhw_setpoint,
        ebusd_circuit="hc1",
        ebusd_message="DHWSetpoint",
    ),
    EbusdNumberDescription(
        key="ebusd_dhw_min",
        translation_key="ebusd_dhw_min",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=20.0,
        native_max_value=50.0,
        native_step=0.5,
        icon="mdi:water-thermometer-outline",
        value_fn=lambda d: d.sensors.dhw_min,
        ebusd_circuit="hc1",
        ebusd_message="DHWMin",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt number entities."""
    conn_type = entry.data.get(CONF_CONNECTION_TYPE, ConnectionType.MODBUS_TCP)
    coordinator = entry.runtime_data

    if conn_type == ConnectionType.EBUSD:
        assert isinstance(coordinator, EbusdDataUpdateCoordinator)
        async_add_entities(
            EbusdNumber(coordinator, desc) for desc in EBUSD_NUMBERS
        )
    else:
        async_add_entities(
            WeishauptNumber(coordinator, desc) for desc in NUMBER_DESCRIPTIONS
        )


class WeishauptNumber(WeishauptEntity, NumberEntity):
    """A Weishaupt number entity for adjustable setpoints."""

    entity_description: WeishauptNumberDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value via Modbus."""
        raw = int(round(value / self.entity_description.scale))
        await self.coordinator.async_write_register(
            self.entity_description.register_address, raw
        )


class EbusdNumber(EbusdEntity, NumberEntity):
    """An ebusd number entity for adjustable user-level setpoints."""

    entity_description: EbusdNumberDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value to ebusd, then refresh."""
        await self.coordinator.async_write_field(
            self.entity_description.ebusd_circuit,
            self.entity_description.ebusd_message,
            value,
        )
