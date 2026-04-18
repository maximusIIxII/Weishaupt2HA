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

from weishaupt_modbus import EbusdData, WeishauptData
from weishaupt_modbus.const import HeatPumpOperationStatus

from .const import CONF_CONNECTION_TYPE, ConnectionType
from .coordinator import (
    EbusdDataUpdateCoordinator,
    WeishauptConfigEntry,
)
from .entity import EbusdEntity, WeishauptEntity


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
#  ebusd binary sensors (gas boilers via eBUS Adapter)
# ══════════════════════════════════════════════════════════

@dataclass(frozen=True, kw_only=True)
class EbusdBinarySensorDescription(BinarySensorEntityDescription):
    """Describes an ebusd binary sensor entity."""

    is_on_fn: Callable[[EbusdData], bool | None]


# Prefixes the WTC uses in the operating_phase enum to flag a fault or warning
# (see J0EK3R f6..sc.csv Operatingphase enum: codes 11–16, 21–24).
# Values like "S:Kesseltemperatur > 105°C", "W:Abgastemperatur > 115°C",
# "W/S:Temperaturdifferenz zu groß" — all match one of these prefixes.
_FAULT_PHASE_PREFIXES: tuple[str, ...] = ("S:", "W:", "W/S:")


def _is_active_fault(phase: str | None) -> bool | None:
    """True when the live operating_phase signals an active fault/warning."""
    if phase is None:
        return None
    return phase.startswith(_FAULT_PHASE_PREFIXES)


EBUSD_BINARY_SENSORS: tuple[EbusdBinarySensorDescription, ...] = (
    EbusdBinarySensorDescription(
        key="ebusd_active_fault",
        translation_key="ebusd_active_fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: _is_active_fault(d.sensors.operating_phase),
    ),
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

    if conn_type == ConnectionType.EBUSD:
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


class EbusdBinarySensor(EbusdEntity, BinarySensorEntity):
    """An ebusd binary sensor entity (eBUS Adapter)."""

    entity_description: EbusdBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)
