"""Base entity for Weishaupt Heat Pump integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WeishauptDataUpdateCoordinator,
)


class WeishauptEntity(CoordinatorEntity[WeishauptDataUpdateCoordinator]):
    """Base class for Weishaupt heat pump entities (Modbus)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WeishauptDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{description.key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this entity."""
        data = self.coordinator.data
        info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Weishaupt Wärmepumpe",
            manufacturer=MANUFACTURER,
        )
        if data and data.device_info:
            info["model"] = data.device_info.device_type
            info["sw_version"] = data.device_info.firmware_version
        return info


class EbusdEntity(CoordinatorEntity[EbusdDataUpdateCoordinator]):
    """Base class for ebusd gas boiler entities (eBUS Adapter)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EbusdDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize the ebusd entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{description.key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this entity."""
        data = self.coordinator.data
        info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Weishaupt Gas-Brennwert (ebusd)",
            manufacturer=MANUFACTURER,
        )
        if data and data.device_info:
            info["model"] = data.device_info.device_name or "WTC"
            info["sw_version"] = data.device_info.ebusd_version
        return info
