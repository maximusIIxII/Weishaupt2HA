"""Base entity for Weishaupt Heat Pump integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import WeishauptDataUpdateCoordinator


class WeishauptEntity(CoordinatorEntity[WeishauptDataUpdateCoordinator]):
    """Base class for all Weishaupt entities."""

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
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Weishaupt Wärmepumpe",
            manufacturer=MANUFACTURER,
            model=data.device_info.device_type if data else None,
            sw_version=data.device_info.firmware_version if data else None,
        )
