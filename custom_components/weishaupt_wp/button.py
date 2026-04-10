"""Button platform for Weishaupt Heat Pump — one-time actions."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus.const import REG_WW_PUSH

from .coordinator import WeishauptConfigEntry, WeishauptDataUpdateCoordinator
from .entity import WeishauptEntity


@dataclass(frozen=True, kw_only=True)
class WeishauptButtonDescription(ButtonEntityDescription):
    """Describes a Weishaupt button entity."""

    press_fn: Callable[
        [WeishauptDataUpdateCoordinator], Coroutine[Any, Any, None]
    ]


async def _press_ww_boost(coordinator: WeishauptDataUpdateCoordinator) -> None:
    """Trigger a one-time hot water boost."""
    await coordinator.async_write_register(REG_WW_PUSH, 1)


BUTTON_DESCRIPTIONS: tuple[WeishauptButtonDescription, ...] = (
    WeishauptButtonDescription(
        key="ww_boost",
        translation_key="ww_boost",
        press_fn=_press_ww_boost,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Weishaupt button entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeishauptButton(coordinator, desc) for desc in BUTTON_DESCRIPTIONS
    )


class WeishauptButton(WeishauptEntity, ButtonEntity):
    """A Weishaupt button entity for one-time actions."""

    entity_description: WeishauptButtonDescription

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator)
