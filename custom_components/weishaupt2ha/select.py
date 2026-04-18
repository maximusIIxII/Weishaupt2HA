"""Select platform for Weishaupt Heat Pump — operation modes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import WeishauptData
from weishaupt_modbus.const import (
    HeatingCircuitMode,
    HeatingCircuitPartyPause,
    REG_HZ_OPERATION_MODE,
    REG_HZ_PARTY_PAUSE,
    REG_SYS_OPERATION_MODE,
    SystemOperationMode,
)

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity


@dataclass(frozen=True, kw_only=True)
class WeishauptSelectDescription(SelectEntityDescription):
    """Describes a Weishaupt select entity."""

    value_fn: Callable[[WeishauptData], int]
    register_address: int
    value_map: dict[int, str]  # register value → display option


# Reverse map: display option → register value
def _reverse_map(m: dict[int, str]) -> dict[str, int]:
    return {v: k for k, v in m.items()}


SYS_MODE_MAP: dict[int, str] = {
    SystemOperationMode.AUTO: "Auto",
    SystemOperationMode.HEATING: "Heizen",
    SystemOperationMode.COOLING: "Kühlen",
    SystemOperationMode.SUMMER: "Sommer",
    SystemOperationMode.STANDBY: "Standby",
    SystemOperationMode.SECOND_HEATER: "2. WEZ",
}

HZ_MODE_MAP: dict[int, str] = {
    HeatingCircuitMode.AUTO: "Auto",
    HeatingCircuitMode.COMFORT: "Komfort",
    HeatingCircuitMode.NORMAL: "Normal",
    HeatingCircuitMode.REDUCED: "Absenk",
    HeatingCircuitMode.STANDBY: "Standby",
}

HZ_PARTY_PAUSE_MAP: dict[int, str] = {
    HeatingCircuitPartyPause.OFF: "Aus",
    HeatingCircuitPartyPause.PARTY: "Party",
    HeatingCircuitPartyPause.PAUSE: "Pause",
}

SELECT_DESCRIPTIONS: tuple[WeishauptSelectDescription, ...] = (
    WeishauptSelectDescription(
        key="sys_operation_mode",
        translation_key="sys_operation_mode",
        value_fn=lambda d: d.system.operation_mode,
        register_address=REG_SYS_OPERATION_MODE,
        value_map=SYS_MODE_MAP,
        options=list(SYS_MODE_MAP.values()),
    ),
    WeishauptSelectDescription(
        key="hz_operation_mode",
        translation_key="hz_operation_mode",
        value_fn=lambda d: d.heating_circuit.operation_mode,
        register_address=REG_HZ_OPERATION_MODE,
        value_map=HZ_MODE_MAP,
        options=list(HZ_MODE_MAP.values()),
    ),
    WeishauptSelectDescription(
        key="hz_party_pause",
        translation_key="hz_party_pause",
        value_fn=lambda d: d.heating_circuit.party_pause,
        register_address=REG_HZ_PARTY_PAUSE,
        value_map=HZ_PARTY_PAUSE_MAP,
        options=list(HZ_PARTY_PAUSE_MAP.values()),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt select entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeishauptSelect(coordinator, desc) for desc in SELECT_DESCRIPTIONS
    )


class WeishauptSelect(WeishauptEntity, SelectEntity):
    """A Weishaupt select entity for operation modes."""

    entity_description: WeishauptSelectDescription

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        raw = self.entity_description.value_fn(self.coordinator.data)
        return self.entity_description.value_map.get(raw)

    async def async_select_option(self, option: str) -> None:
        """Set the selected option via Modbus."""
        reverse = _reverse_map(self.entity_description.value_map)
        raw = reverse.get(option)
        if raw is not None:
            await self.coordinator.async_write_register(
                self.entity_description.register_address, raw
            )
