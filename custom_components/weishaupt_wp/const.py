"""Constants for the Weishaupt Heat Pump integration."""

from datetime import timedelta

DOMAIN = "weishaupt_wp"
MANUFACTURER = "Weishaupt"

DEFAULT_HOST = ""
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

PLATFORMS = [
    "climate",
    "sensor",
    "number",
    "select",
    "binary_sensor",
    "water_heater",
]
