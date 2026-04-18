"""Async communication library for Weishaupt heating systems.

Supports:
- Modbus TCP via WCM-COM for heat pumps (WBB series)
- ebusd TCP for eBUS Adapter hardware (WTC series)
"""

from .client import WeishauptModbusClient
from .ebusd_client import WeishauptEbusdClient
from .ebusd_models import (
    EbusdData,
    EbusdDeviceInfo,
    EbusdSensorData,
)
from .exceptions import (
    WeishauptConnectionError,
    WeishauptModbusError,
    WeishauptReadError,
    WeishauptWriteError,
)
from .models import (
    DeviceInfo,
    HeatingCircuitData,
    HeatPumpData,
    HotWaterData,
    SecondaryHeaterData,
    StatisticsData,
    SystemData,
    WeishauptData,
)

__all__ = [
    # Modbus client (heat pumps)
    "WeishauptModbusClient",
    "DeviceInfo",
    "HeatingCircuitData",
    "HeatPumpData",
    "HotWaterData",
    "SecondaryHeaterData",
    "StatisticsData",
    "SystemData",
    "WeishauptData",
    # ebusd client (eBUS adapter)
    "WeishauptEbusdClient",
    "EbusdData",
    "EbusdDeviceInfo",
    "EbusdSensorData",
    # Exceptions
    "WeishauptModbusError",
    "WeishauptConnectionError",
    "WeishauptReadError",
    "WeishauptWriteError",
]
