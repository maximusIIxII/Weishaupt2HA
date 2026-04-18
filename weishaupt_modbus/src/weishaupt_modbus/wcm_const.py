"""Constants for WCM-COM HTTP API (coco protocol) communication."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

# Connection defaults
DEFAULT_HTTP_PORT = 80
DEFAULT_TIMEOUT = 10
DEFAULT_SCAN_INTERVAL = 30

# coco protocol constants
COCO_PROTOCOL = "coco"
CMD_READ = 1
CMD_WRITE = 2
CMD_ERROR = 255

# Protocol types
PROT_STANDARD = 0
PROT_GENERIC = 1

# Sentinel value for "not available" (0x8000)
VALUE_NOT_AVAILABLE = 0x8000

# Maximum telegrams per request (WCM-COM limitation)
MAX_TELEGRAMS_PER_REQUEST = 25


class ModuleType(IntEnum):
    """WCM-COM module types on the eBUS."""

    SYSTEM = 0
    WTC_G = 10       # WTC Gas boiler / heat exchanger
    WCM_SOL = 3      # Solar module


class WTCOperatingPhase(IntEnum):
    """WTC operating phases (INFONR 373)."""

    STANDBY = 0
    HEATING = 1
    HOT_WATER = 2
    UNKNOWN = 255


# ──────────────────────────────────────────────────────────
#  WCM-COM Parameter definitions (INFONR values)
# ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ParamDef:
    """Definition of a WCM-COM parameter."""

    infonr: int
    name: str
    unit: str
    scale: float = 1.0       # divisor (10=temp, 100=flow, 1=raw)
    module_type: int = 0     # default: SYSTEM
    signed: bool = True
    writable: bool = False


# ── Temperatures (scale /10) ──
PARAM_ERROR_CODE = ParamDef(1, "error_code", "", scale=1, signed=False)
PARAM_HEAT_REQUEST = ParamDef(2, "heat_request", "°C", scale=10)
PARAM_OUTDOOR_TEMP = ParamDef(12, "outdoor_temp", "°C", scale=10)
PARAM_FLOW_TEMP = ParamDef(13, "flow_temp", "°C", scale=10)
PARAM_HOT_WATER_TEMP = ParamDef(14, "hot_water_temp", "°C", scale=10)
PARAM_BUFFER_TOP_TEMP = ParamDef(118, "buffer_top_temp", "°C", scale=10)
PARAM_BUFFER_BOTTOM_TEMP = ParamDef(120, "buffer_bottom_temp", "°C", scale=10)
PARAM_EXHAUST_TEMP = ParamDef(325, "exhaust_temp", "°C", scale=10)
PARAM_DAMPED_OUTDOOR_TEMP = ParamDef(2572, "damped_outdoor_temp", "°C", scale=10)
PARAM_RETURN_TEMP = ParamDef(3101, "return_temp", "°C", scale=10)

# ── Flow & Power (scale /100) ──
PARAM_FLOW_RATE = ParamDef(130, "flow_rate", "l/min", scale=100)
PARAM_SOLAR_POWER = ParamDef(475, "solar_power", "W", scale=100)
PARAM_LOAD_SETTING_KW = ParamDef(4176, "load_setting_kw", "kW", scale=10)

# ── Raw values ──
PARAM_LOAD_POSITION = ParamDef(138, "load_position", "%", scale=1, signed=False)
PARAM_OPERATING_PHASE = ParamDef(373, "operating_phase", "", scale=1, signed=False)
PARAM_BURNER_HOURS = ParamDef(3198, "burner_hours", "h", scale=1, signed=False)
PARAM_BURNER_CYCLES = ParamDef(3196, "burner_cycles", "", scale=1, signed=False)
PARAM_BURNER_STAGE1_HOURS = ParamDef(3159, "burner_stage1_hours", "h", scale=1, signed=False)
PARAM_BURNER_STAGE1_CYCLES = ParamDef(3158, "burner_stage1_cycles", "", scale=1, signed=False)
PARAM_OIL_METER_HIGH = ParamDef(3792, "oil_meter_high", "", scale=1, signed=False)
PARAM_OIL_METER_LOW = ParamDef(3793, "oil_meter_low", "l", scale=1, signed=False)
PARAM_COMM_MODULE_TYPE = ParamDef(328, "comm_module_type", "", scale=1, signed=False)

# ── Solar (module type 3) ──
PARAM_SOLAR_COLLECTOR_TEMP = ParamDef(2601, "solar_collector_temp", "°C", scale=10, module_type=3)
PARAM_SOLAR_BOTTOM_TEMP = ParamDef(2602, "solar_bottom_temp", "°C", scale=10, module_type=3)

# ── WCM-COM System Info (module type 0) ──
PARAM_DEVICE_NAME = ParamDef(5066, "device_name", "", scale=0)
PARAM_DEVICE_TYPE_ID = ParamDef(5067, "device_type_id", "", scale=1, signed=False)
PARAM_OWNER_NAME = ParamDef(5068, "owner_name", "", scale=0)
PARAM_HOSTNAME = ParamDef(5090, "hostname", "", scale=0)
PARAM_FIRMWARE = ParamDef(5010, "firmware_version", "", scale=1, signed=False)

# ──────────────────────────────────────────────────────────
#  Parameter groups for batch reading
# ──────────────────────────────────────────────────────────

# Core sensor parameters (always polled)
SENSOR_PARAMS: list[ParamDef] = [
    PARAM_ERROR_CODE,
    PARAM_HEAT_REQUEST,
    PARAM_OUTDOOR_TEMP,
    PARAM_FLOW_TEMP,
    PARAM_HOT_WATER_TEMP,
    PARAM_BUFFER_TOP_TEMP,
    PARAM_BUFFER_BOTTOM_TEMP,
    PARAM_FLOW_RATE,
    PARAM_LOAD_POSITION,
    PARAM_EXHAUST_TEMP,
    PARAM_OPERATING_PHASE,
    PARAM_DAMPED_OUTDOOR_TEMP,
    PARAM_RETURN_TEMP,
    PARAM_LOAD_SETTING_KW,
]

# Statistics parameters (polled less frequently)
STATS_PARAMS: list[ParamDef] = [
    PARAM_BURNER_HOURS,
    PARAM_BURNER_CYCLES,
    PARAM_OIL_METER_HIGH,
    PARAM_OIL_METER_LOW,
]

# Device info parameters (polled once at startup)
DEVICE_INFO_PARAMS: list[ParamDef] = [
    PARAM_DEVICE_NAME,
    PARAM_DEVICE_TYPE_ID,
    PARAM_HOSTNAME,
    PARAM_FIRMWARE,
]
