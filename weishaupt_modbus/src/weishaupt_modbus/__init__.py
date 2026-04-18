"""Async communication library for Weishaupt heating systems.

Supports:
- Modbus TCP via WCM-COM for heat pumps (WBB series)
- HTTP coco protocol via WCM-COM for gas boilers (WTC series)
- ebusd TCP for eBUS Adapter hardware (WTC series)
"""

from .client import WeishauptModbusClient
from .ebusd_client import WeishauptEbusdClient
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
from .wcm_client import WeishauptWCMClient
from .wcm_models import (
    WCMData,
    WCMDeviceInfo,
    WTCSensorData,
    WTCStatisticsData,
)
from .ebusd_models import (
    EbusdData,
    EbusdDeviceInfo,
    EbusdSensorData,
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
    # HTTP/WCM client (gas boilers)
    "WeishauptWCMClient",
    "WCMData",
    "WCMDeviceInfo",
    "WTCSensorData",
    "WTCStatisticsData",
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
