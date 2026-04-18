"""Binary sensor platform for Weishaupt Heat Pump / Gas Boiler."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weishaupt_modbus import EbusdData, WCMData, WeishauptData
from weishaupt_modbus.const import HeatPumpOperationStatus

from .const import CONF_CONNECTION_TYPE, ConnectionType
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WCMDataUpdateCoordinator,
    WeishauptConfigEntry,
)
from .entity import EbusdEntity, WCMEntity, WeishauptEntity


# ══════════════════════════════════════════════════════════
#  Modbus TCP binary sensors (heat pumps)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class WeishauptBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a Weishaupt binary sensor entity."""

    is_on_fn: Callable[[WeishauptData], bool | None]


MODBUS_BINARY_SENSORS: tuple[WeishauptBinarySensorDescription, ...] = (
    WeishauptBinarySensorDescription(
        key="hp_compressor_active",
        translation_key="hp_compressor_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.heat_pump.operation_status in (
            HeatPumpOperationStatus.HEATING,
            HeatPumpOperationStatus.HOT_WATER,
            HeatPumpOperationStatus.COOLING,
        ),
    ),
    WeishauptBinarySensorDescription(
        key="hp_defrost_active",
        translation_key="hp_defrost_active",
        is_on_fn=lambda d: d.heat_pump.operation_status == HeatPumpOperationStatus.DEFROST,
    ),
    WeishauptBinarySensorDescription(
        key="hp_error",
        translation_key="hp_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.system.error_code != 65535,
    ),
    WeishauptBinarySensorDescription(
        key="hp_warning",
        translation_key="hp_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.system.warning_code != 65535,
    ),
    WeishauptBinarySensorDescription(
        key="w2_eheater1_active",
        translation_key="w2_eheater1_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.secondary_heater.eheater1_status != 0,
    ),
    WeishauptBinarySensorDescription(
        key="w2_eheater2_active",
        translation_key="w2_eheater2_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda d: d.secondary_heater.eheater2_status != 0,
    ),
)


# ══════════════════════════════════════════════════════════
#  WCM-COM HTTP binary sensors (gas boilers)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class WCMBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a WCM-COM binary sensor entity."""

    is_on_fn: Callable[[WCMData], bool | None]


# ══════════════════════════════════════════════════════════
#  ebusd binary sensors (gas boilers via eBUS Adapter)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class EbusdBinarySensorDescription(BinarySensorEntityDescription):
    """Describes an ebusd binary sensor entity."""

    is_on_fn: Callable[[EbusdData], bool | None]


EBUSD_BINARY_SENSORS: tuple[EbusdBinarySensorDescription, ...] = (
    EbusdBinarySensorDescription(
        key="ebusd_flame_active",
        translation_key="ebusd_flame_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:fire",
        is_on_fn=lambda d: (
            d.sensors.flame_active is not None
            and d.sensors.flame_active > 0
        ),
    ),
    EbusdBinarySensorDescription(
        key="ebusd_pump_active",
        translation_key="ebusd_pump_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
        is_on_fn=lambda d: (
            d.sensors.pump_active is not None
            and d.sensors.pump_active > 0
        ),
    ),
    EbusdBinarySensorDescription(
        key="ebusd_error",
        translation_key="ebusd_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: (
            d.sensors.error_active is not None
            and d.sensors.error_active > 0
        ),
    ),
    EbusdBinarySensorDescription(
        key="ebusd_gas_valve1_active",
        translation_key="ebusd_gas_valve1_active",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:valve",
        entity_registry_enabled_default=False,
        is_on_fn=lambda d: (
            d.sensors.gas_valve1_active is not None
            and d.sensors.gas_valve1_active > 0
        ),
    ),
    EbusdBinarySensorDescription(
        key="ebusd_gas_valve2_active",
        translation_key="ebusd_gas_valve2_active",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:valve",
        entity_registry_enabled_default=False,
        is_on_fn=lambda d: (
            d.sensors.gas_valve2_active is not None
            and d.sensors.gas_valve2_active > 0
        ),
    ),
)


WCM_BINARY_SENSORS: tuple[WCMBinarySensorDescription, ...] = (
    WCMBinarySensorDescription(
        key="wcm_burner_active",
        translation_key="wcm_burner_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:fire",
        is_on_fn=lambda d: (
            d.sensors.operating_phase is not None
            and d.sensors.operating_phase > 0
        ),
    ),
    WCMBinarySensorDescription(
        key="wcm_heating_active",
        translation_key="wcm_heating_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:radiator",
        is_on_fn=lambda d: d.sensors.operating_phase == 1,
    ),
    WCMBinarySensorDescription(
        key="wcm_hot_water_active",
        translation_key="wcm_hot_water_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-boiler",
        is_on_fn=lambda d: d.sensors.operating_phase == 2,
    ),
    WCMBinarySensorDescription(
        key="wcm_error",
        translation_key="wcm_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.sensors.error_code != 0,
    ),
)


# ══════════════════════════════════════════════════════════
#  Platform setup
# ══════════════════════════════════════════════════════════

async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeishauptConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    conn_type = entry.data.get(CONF_CONNECTION_TYPE, ConnectionType.MODBUS_TCP)

    if conn_type == ConnectionType.WCM_HTTP:
        coordinator = entry.runtime_data
        assert isinstance(coordinator, WCMDataUpdateCoordinator)
        async_add_entities(
            WCMBinarySensor(coordinator, desc) for desc in WCM_BINARY_SENSORS
        )
    elif conn_type == ConnectionType.EBUSD:
        coordinator = entry.runtime_data
        assert isinstance(coordinator, EbusdDataUpdateCoordinator)
        async_add_entities(
            EbusdBinarySensor(coordinator, desc) for desc in EBUSD_BINARY_SENSORS
        )
    else:
        coordinator = entry.runtime_data
        async_add_entities(
            WeishauptBinarySensor(coordinator, desc) for desc in MODBUS_BINARY_SENSORS
        )


class WeishauptBinarySensor(WeishauptEntity, BinarySensorEntity):
    """A Weishaupt binary sensor entity (Modbus)."""

    entity_description: WeishauptBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)


class WCMBinarySensor(WCMEntity, BinarySensorEntity):
    """A WCM-COM binary sensor entity (HTTP)."""

    entity_description: WCMBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)


class EbusdBinarySensor(EbusdEntity, BinarySensorEntity):
    """An ebusd binary sensor entity (eBUS Adapter)."""

    entity_description: EbusdBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)
