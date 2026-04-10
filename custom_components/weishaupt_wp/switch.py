"""Switch platform for Weishaupt Heat Pump."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import WeishauptData
from weishaupt_modbus.const import REG_HP_QUIET_MODE, REG_WW_PUSH

from .coordinator import WeishauptConfigEntry
from .entity import WeishauptEntity


@dataclass(frozen=True, kw_only=True)
class WeishauptSwitchDescription(SwitchEntityDescription):
    """Describes a Weishaupt switch entity."""

    is_on_fn: Callable[[WeishauptData], bool]
    register_address: int
    on_value: int = 1
    off_value: int = 0


SWITCH_DESCRIPTIONS: tuple[WeishauptSwitchDescription, ...] = (
    WeishauptSwitchDescription(
        key="hp_quiet_mode",
        translation_key="hp_quiet_mode",
        is_on_fn=lambda d: d.heat_pump.quiet_mode != 0,
        register_address=REG_HP_QUIET_MODE,
    ),
    WeishauptSwitchDescription(
        key="ww_push",
        translation_key="ww_push",
        is_on_fn=lambda d: d.hot_water.push_active != 0,
        register_address=REG_WW_PUSH,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt switch entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeishauptSwitch(coordinator, desc) for desc in SWITCH_DESCRIPTIONS
    )


class WeishauptSwitch(WeishauptEntity, SwitchEntity):
    """A Weishaupt switch entity."""

    entity_description: WeishauptSwitchDescription

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.async_write_register(
            self.entity_description.register_address,
            self.entity_description.on_value,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.async_write_register(
            self.entity_description.register_address,
            self.entity_description.off_value,
        )
