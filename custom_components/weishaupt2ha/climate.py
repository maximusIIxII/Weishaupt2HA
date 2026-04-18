"""Climate platform for Weishaupt Heat Pump — Heating Circuit."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus.const import (
    HeatingCircuitMode,
    HeatPumpOperationStatus,
    REG_HZ_COMFORT_TEMP,
    REG_HZ_OPERATION_MODE,
    TEMPERATURE_SCALE,
)

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity

# Map Weishaupt modes → HA HVAC modes
_WH_TO_HVAC: dict[int, HVACMode] = {
    HeatingCircuitMode.STANDBY: HVACMode.OFF,
    HeatingCircuitMode.AUTO: HVACMode.AUTO,
    HeatingCircuitMode.COMFORT: HVACMode.HEAT,
    HeatingCircuitMode.NORMAL: HVACMode.HEAT,
    HeatingCircuitMode.REDUCED: HVACMode.HEAT,
}

# Map HA HVAC modes → Weishaupt modes
_HVAC_TO_WH: dict[HVACMode, int] = {
    HVACMode.OFF: HeatingCircuitMode.STANDBY,
    HVACMode.AUTO: HeatingCircuitMode.AUTO,
    HVACMode.HEAT: HeatingCircuitMode.COMFORT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Weishaupt climate entity."""
    coordinator = entry.runtime_data
    async_add_entities([WeishauptClimate(coordinator)])


class WeishauptClimate(WeishauptEntity, ClimateEntity):
    """Climate entity for the Weishaupt heating circuit."""

    _attr_translation_key = "heating_circuit"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 10.0
    _attr_max_temp = 30.0
    _enable_turn_on_off_backwards_compat = False

    def __init__(self, coordinator) -> None:
        """Initialize the climate entity."""
        from homeassistant.helpers.entity import EntityDescription

        desc = EntityDescription(key="heating_circuit")
        super().__init__(coordinator, desc)

    @property
    def current_temperature(self) -> float | None:
        """Return the current room temperature."""
        return self.coordinator.data.heating_circuit.room_temp

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.data.heating_circuit.comfort_temp

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        wh_mode = self.coordinator.data.heating_circuit.operation_mode
        return _WH_TO_HVAC.get(wh_mode, HVACMode.AUTO)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running action."""
        hp_status = self.coordinator.data.heat_pump.operation_status
        if hp_status == HeatPumpOperationStatus.HEATING:
            return HVACAction.HEATING
        if hp_status == HeatPumpOperationStatus.COOLING:
            return HVACAction.COOLING
        if hp_status == HeatPumpOperationStatus.OFF:
            return HVACAction.OFF
        if hp_status == HeatPumpOperationStatus.STANDBY:
            return HVACAction.IDLE
        if hp_status == HeatPumpOperationStatus.DEFROST:
            return HVACAction.DEFROSTING
        return HVACAction.IDLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        raw_value = int(round(temp / TEMPERATURE_SCALE))
        await self.coordinator.async_write_register(REG_HZ_COMFORT_TEMP, raw_value)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        wh_mode = _HVAC_TO_WH.get(hvac_mode)
        if wh_mode is None:
            return
        await self.coordinator.async_write_register(REG_HZ_OPERATION_MODE, wh_mode)
