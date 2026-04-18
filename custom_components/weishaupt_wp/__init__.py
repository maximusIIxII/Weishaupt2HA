"""The Weishaupt Heat Pump integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CONNECTION_TYPE,
    CONF_EBUSD_CIRCUIT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    ConnectionType,
    PLATFORMS_EBUSD,
    PLATFORMS_MODBUS,
    PLATFORMS_WCM,
)
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WCMDataUpdateCoordinator,
    WeishauptConfigEntry,
    WeishauptDataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)


def _get_platforms(entry: ConfigEntry) -> list[str]:
    """Return the platform list based on connection type."""
    conn_type = entry.data.get(CONF_CONNECTION_TYPE, ConnectionType.MODBUS_TCP)
    if conn_type == ConnectionType.WCM_HTTP:
        return PLATFORMS_WCM
    if conn_type == ConnectionType.EBUSD:
        return PLATFORMS_EBUSD
    return PLATFORMS_MODBUS


async def async_setup_entry(hass: HomeAssistant, entry: WeishauptConfigEntry) -> bool:
    """Set up Weishaupt Heat Pump from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    conn_type = entry.data.get(CONF_CONNECTION_TYPE, ConnectionType.MODBUS_TCP)

    if conn_type == ConnectionType.WCM_HTTP:
        # WCM-COM HTTP client for gas boilers
        from weishaupt_modbus import WeishauptWCMClient

        username = entry.data.get(CONF_USERNAME, "admin")
        password = entry.data.get(CONF_PASSWORD, "")
        client = WeishauptWCMClient(
            host=host, port=port, username=username, password=password
        )
        coordinator = WCMDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=scan_interval),
        )
    elif conn_type == ConnectionType.EBUSD:
        # ebusd TCP client for eBUS adapter
        from weishaupt_modbus import WeishauptEbusdClient

        circuit = entry.data.get(CONF_EBUSD_CIRCUIT, "")
        client = WeishauptEbusdClient(
            host=host, port=port, circuit=circuit
        )
        coordinator = EbusdDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=scan_interval),
        )
    else:
        # Modbus TCP client for heat pumps
        from weishaupt_modbus import WeishauptModbusClient

        slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
        client = WeishauptModbusClient(host=host, port=port, slave_id=slave_id)
        coordinator = WeishauptDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=scan_interval),
        )

    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    platforms = _get_platforms(entry)
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: WeishauptConfigEntry) -> bool:
    """Unload a config entry."""
    platforms = _get_platforms(entry)
    return await hass.config_entries.async_unload_platforms(entry, platforms)


async def _async_update_listener(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update — reload the integration."""
    await hass.config_entries.async_reload(entry.entry_id)
