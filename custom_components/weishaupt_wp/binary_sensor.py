"""Binary sensor platform for Weishaupt Heat Pump."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import WeishauptData
from weishaupt_modbus.const import HeatPumpOperationStatus

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity


@dataclass(frozen=True, kw_only=True)
class WeishauptBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a Weishaupt binary sensor entity."""

    is_on_fn: Callable[[WeishauptData], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[WeishauptBinarySensorDescription, ...] = (
    WeishauptBinarySensorDescription(
        key="hp_compressor_active",
        translation_key="hp_compressor_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.heat_pump.operation_status in (
            HeatPumpOperationStatus.HEATING,
            HeatPumpOperationStatus.HOT_WATER,
            HeatPumpOperationStatus.COOLING,
        ),
    ),
    WeishauptBinarySensorDescription(
        key="hp_defrost_active",
        translation_key="hp_defrost_active",
        is_on_fn=lambda d: d.heat_pump.operation_status == HeatPumpOperationStatus.DEFROST,
    ),
    WeishauptBinarySensorDescription(
        key="hp_error",
        translation_key="hp_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.system.error_code != 65535,
    ),
    WeishauptBinarySensorDescription(
        key="hp_warning",
        translation_key="hp_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.system.warning_code != 65535,
    ),
    WeishauptBinarySensorDescription(
        key="w2_eheater1_active",
        translation_key="w2_eheater1_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.secondary_heater.eheater1_status != 0,
    ),
    WeishauptBinarySensorDescription(
        key="w2_eheater2_active",
        translation_key="w2_eheater2_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.secondary_heater.eheater2_status != 0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt binary sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeishauptBinarySensor(coordinator, desc) for desc in BINARY_SENSOR_DESCRIPTIONS
    )


class WeishauptBinarySensor(WeishauptEntity, BinarySensorEntity):
    """A Weishaupt binary sensor entity."""

    entity_description: WeishauptBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)
