"""Constants for the Weishaupt Heat Pump integration."""

from datetime import timedelta
from enum import StrEnum

DOMAIN = "weishaupt_wp"
MANUFACTURER = "Weishaupt"

DEFAULT_HOST = ""
DEFAULT_PORT = 502
DEFAULT_EBUSD_PORT = 8888
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CONNECTION_TYPE = "connection_type"
CONF_EBUSD_CIRCUIT = "ebusd_circuit"

MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300


class ConnectionType(StrEnum):
    """Connection type to the Weishaupt heating system."""

    MODBUS_TCP = "modbus_tcp"   # Heat pumps (WBB) via Modbus TCP
    EBUSD = "ebusd"             # Gas boilers (WTC) via eBUS Adapter + ebusd


# Platforms for Modbus TCP (heat pumps)
PLATFORMS_MODBUS = [
    "binary_sensor",
    "button",
    "climate",
    "number",
    "select",
    "sensor",
    "switch",
    "water_heater",
]

# Platforms for ebusd (gas boilers via eBUS adapter)
PLATFORMS_EBUSD = [
    "binary_sensor",
    "number",
    "sensor",
]

# Legacy fallback
PLATFORMS = PLATFORMS_MODBUS
