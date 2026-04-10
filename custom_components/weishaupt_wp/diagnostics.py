"""Diagnostics support for Weishaupt Heat Pump."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .coordinator import WeishauptConfigEntry

REDACT_KEYS = {CONF_HOST}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: WeishauptConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data = coordinator.data

    return {
        "config_entry": async_redact_data(dict(entry.data), REDACT_KEYS),
        "options": dict(entry.options),
        "data": asdict(data) if data else None,
    }
