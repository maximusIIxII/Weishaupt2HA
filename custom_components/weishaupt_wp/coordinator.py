"""DataUpdateCoordinator for Weishaupt Heat Pump / Gas Boiler."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Union

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from weishaupt_modbus import (
    EbusdData,
    WeishauptData,
    WeishauptEbusdClient,
    WeishauptModbusClient,
)
from weishaupt_modbus.ebusd_models import EbusdDeviceInfo
from weishaupt_modbus.exceptions import WeishauptModbusError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Union type for all data models
WeishauptAllData = Union[WeishauptData, EbusdData]

type WeishauptConfigEntry = ConfigEntry[
    "WeishauptDataUpdateCoordinator | EbusdDataUpdateCoordinator"
]


class WeishauptDataUpdateCoordinator(DataUpdateCoordinator[WeishauptData]):
    """Coordinator to manage data fetching from a Weishaupt heat pump (Modbus)."""

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


class EbusdDataUpdateCoordinator(DataUpdateCoordinator[EbusdData]):
    """Coordinator to manage data fetching via ebusd (eBUS Adapter)."""

    config_entry: WeishauptConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeishauptEbusdClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the ebusd coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_ebusd",
            update_interval=update_interval,
        )
        self.client = client
        self._device_info: EbusdDeviceInfo | None = None

    async def _async_update_data(self) -> EbusdData:
        """Fetch all data from ebusd."""
        try:
            if self._device_info is None:
                self._device_info = await self.client.async_identify_device()
            data = await self.client.async_read_all()
            data.device_info = self._device_info
            return data
        except WeishauptModbusError as err:
            raise UpdateFailed(f"Error communicating with ebusd: {err}") from err

    async def async_shutdown(self) -> None:
        """Disconnect from ebusd on shutdown."""
        await super().async_shutdown()
        await self.client.disconnect()
