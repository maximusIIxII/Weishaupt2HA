"""Water heater platform for Weishaupt Heat Pump — Hot Water."""

from __future__ import annotations

from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus.const import (
    REG_WW_NORMAL_TEMP,
    REG_WW_PUSH,
    TEMPERATURE_SCALE,
)

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity

OPERATION_ECO = "eco"
OPERATION_NORMAL = "normal"
OPERATION_BOOST = "boost"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Weishaupt water heater entity."""
    coordinator = entry.runtime_data
    async_add_entities([WeishauptWaterHeater(coordinator)])


class WeishauptWaterHeater(WeishauptEntity, WaterHeaterEntity):
    """Water heater entity for Weishaupt hot water."""

    _attr_translation_key = "hot_water"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_operation_list = [OPERATION_ECO, OPERATION_NORMAL, OPERATION_BOOST]
    _attr_min_temp = 30.0
    _attr_max_temp = 65.0

    def __init__(self, coordinator) -> None:
        """Initialize the water heater entity."""
        desc = EntityDescription(key="hot_water")
        super().__init__(coordinator, desc)

    @property
    def current_temperature(self) -> float | None:
        """Return the current hot water temperature."""
        return self.coordinator.data.hot_water.current_temp

    @property
    def target_temperature(self) -> float | None:
        """Return the target hot water temperature."""
        return self.coordinator.data.hot_water.normal_temp

    @property
    def current_operation(self) -> str:
        """Return the current operation mode."""
        ww = self.coordinator.data.hot_water
        if ww.push_active:
            return OPERATION_BOOST
        if ww.normal_temp <= ww.reduced_temp:
            return OPERATION_ECO
        return OPERATION_NORMAL

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target hot water temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        raw_value = int(round(temp / TEMPERATURE_SCALE))
        await self.coordinator.async_write_register(REG_WW_NORMAL_TEMP, raw_value)

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the operation mode."""
        if operation_mode == OPERATION_BOOST:
            await self.coordinator.async_write_register(REG_WW_PUSH, 1)
        elif operation_mode == OPERATION_ECO:
            await self.coordinator.async_write_register(REG_WW_PUSH, 0)
            # Set normal temp to reduced temp level
            reduced = self.coordinator.data.hot_water.reduced_temp
            raw = int(round(reduced / TEMPERATURE_SCALE))
            await self.coordinator.async_write_register(REG_WW_NORMAL_TEMP, raw)
        elif operation_mode == OPERATION_NORMAL:
            await self.coordinator.async_write_register(REG_WW_PUSH, 0)
