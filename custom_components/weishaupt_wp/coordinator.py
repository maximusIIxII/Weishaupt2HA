"""DataUpdateCoordinator for Weishaupt Heat Pump."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from weishaupt_modbus import WeishauptData, WeishauptModbusClient
from weishaupt_modbus.exceptions import WeishauptModbusError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

type WeishauptConfigEntry = ConfigEntry[WeishauptDataUpdateCoordinator]


class WeishauptDataUpdateCoordinator(DataUpdateCoordinator[WeishauptData]):
    """Coordinator to manage data fetching from a Weishaupt heat pump."""

    config_entry: WeishauptConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeishauptModbusClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> WeishauptData:
        """Fetch all data from the heat pump in one batch."""
        try:
            return await self.client.async_read_all()
        except WeishauptModbusError as err:
            raise UpdateFailed(f"Error communicating with heat pump: {err}") from err

    async def async_write_register(self, address: int, value: int) -> None:
        """Write a register and refresh data."""
        try:
            await self.client.async_write_register(address, value)
        except WeishauptModbusError as err:
            raise UpdateFailed(f"Error writing register {address}: {err}") from err
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Disconnect from the heat pump on shutdown."""
        await super().async_shutdown()
        await self.client.disconnect()
