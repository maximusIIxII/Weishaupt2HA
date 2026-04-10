"""Constants and enums for Weishaupt Modbus communication."""

from __future__ import annotations

from enum import IntEnum, StrEnum

# Connection defaults
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_TIMEOUT = 5

# Temperature values are stored as int * 10 (e.g. 215 = 21.5°C)
TEMPERATURE_SCALE = 0.1
ENERGY_SCALE = 0.1
PERCENTAGE_SCALE = 1


class SystemOperationMode(IntEnum):
    """System operation modes (Register 40001)."""

    AUTO = 0
    HEATING = 1
    COOLING = 2
    SUMMER = 3
    STANDBY = 4
    SECOND_HEATER = 5


class HotWaterPush(IntEnum):
    """Hot water push modes (Register 42102)."""

    OFF = 0
    ON = 1


class HeatingCircuitMode(IntEnum):
    """Heating circuit operation modes (Register 41103)."""

    AUTO = 0
    COMFORT = 1
    NORMAL = 2
    REDUCED = 3
    STANDBY = 4


class HeatingCircuitPartyPause(IntEnum):
    """Heating circuit party/pause modes (Register 41104)."""

    OFF = 0
    PARTY = 1
    PAUSE = 2


class HeatPumpOperationStatus(IntEnum):
    """Heat pump operation status (Register 33101)."""

    UNDETERMINED = -1
    STANDBY = 0
    HEATING = 1
    HOT_WATER = 2
    DEFROST = 3
    OFF = 4
    COOLING = 5


class HeatPumpErrorStatus(IntEnum):
    """Heat pump error status (Register 33102)."""

    NONE = 0
    ERROR = 1
    WARNING = 2


class SystemDisplayStatus(IntEnum):
    """System display status (Register 30006)."""

    UNDETERMINED = -1
    OFF = 0
    HEATING = 1
    HOT_WATER = 2
    DEFROST = 3
    STANDBY = 4
    COOLING = 5


class SecondaryHeaterStatus(IntEnum):
    """Secondary heater status (Register 34101)."""

    OFF = 0
    ON = 1


# ──────────────────────────────────────────────────────────
#  Register address map
# ──────────────────────────────────────────────────────────

class RegisterGroup(StrEnum):
    """Register groups / device areas."""

    SYSTEM = "system"
    HEAT_PUMP = "heat_pump"
    HOT_WATER = "hot_water"
    HEATING_CIRCUIT = "heating_circuit"
    HEATING_CIRCUIT_2 = "heating_circuit_2"
    SECONDARY_HEATER = "secondary_heater"
    IO = "io"
    STATISTICS = "statistics"


# ── System (SYS) ──
# Input registers (read-only)
REG_SYS_OUTDOOR_TEMP = 30001
REG_SYS_AIR_INTAKE_TEMP = 30002
REG_SYS_ERROR = 30003
REG_SYS_WARNING = 30004
REG_SYS_ERROR_FREE = 30005
REG_SYS_DISPLAY_STATUS = 30006
# Holding registers (read-write)
REG_SYS_OPERATION_MODE = 40001
REG_SYS_PV_SETPOINT = 40002

# ── Heat Pump (WP) ──
REG_HP_OPERATION_STATUS = 33101
REG_HP_ERROR_STATUS = 33102
REG_HP_POWER_REQUEST = 33103  # Also used for calculated thermal power
REG_HP_FLOW_TEMP = 33104
REG_HP_RETURN_TEMP = 33105
REG_HP_EVAPORATOR_TEMP = 33106
REG_HP_COMPRESSOR_INTAKE_TEMP = 33107
REG_HP_SWITCH_TEMP = 33108
REG_HP_REQUEST_REGEN = 33109
REG_HP_BUFFER_TEMP = 33110
REG_HP_PRECISE_FLOW_TEMP = 33111
# Holding registers (read-only via NUMBER_RO)
REG_HP_CONFIG = 43101
REG_HP_QUIET_MODE = 43102
REG_HP_PUMP_START_MODE = 43103
REG_HP_PUMP_POWER_HEATING = 43104
REG_HP_PUMP_POWER_COOLING = 43105
REG_HP_PUMP_POWER_HOT_WATER = 43106
REG_HP_PUMP_POWER_DEFROST = 43107
REG_HP_FLOW_RATE_HEATING = 43108
REG_HP_FLOW_RATE_COOLING = 43109
REG_HP_FLOW_RATE_HOT_WATER = 43110

# ── Hot Water (WW) ──
REG_WW_TARGET_TEMP = 32101
REG_WW_CURRENT_TEMP = 32102
# Holding registers
REG_WW_CONFIG = 42101
REG_WW_PUSH = 42102
REG_WW_NORMAL_TEMP = 42103
REG_WW_REDUCED_TEMP = 42104
REG_WW_SG_READY_BOOST = 42105

# ── Heating Circuit (HZ) ──
REG_HZ_ROOM_TARGET_TEMP = 31101
REG_HZ_ROOM_TEMP = 31102
REG_HZ_ROOM_HUMIDITY = 31103
REG_HZ_FLOW_TARGET_TEMP = 31104
REG_HZ_FLOW_TEMP = 31105
# Holding registers
REG_HZ_CONFIG = 41101
REG_HZ_REQUEST_TYPE = 41102
REG_HZ_OPERATION_MODE = 41103
REG_HZ_PARTY_PAUSE = 41104
REG_HZ_COMFORT_TEMP = 41105
REG_HZ_NORMAL_TEMP = 41106
REG_HZ_REDUCED_TEMP = 41107
REG_HZ_HEATING_CURVE = 41108
REG_HZ_SUMMER_WINTER_SWITCH = 41109
REG_HZ_CONST_TEMP_HEATING = 41110
REG_HZ_CONST_TEMP_REDUCED = 41111
REG_HZ_CONST_TEMP_COOLING = 41112

# ── Secondary Heater (W2) ──
REG_W2_STATUS = 34101
REG_W2_EHEATER1_CYCLES = 34102
REG_W2_EHEATER1_HOURS = 34103
REG_W2_EHEATER1_STATUS = 34104
REG_W2_EHEATER2_STATUS = 34105
REG_W2_EHEATER2_CYCLES = 34106
REG_W2_EHEATER2_HOURS = 34107
# Holding registers
REG_W2_CONFIG = 44101
REG_W2_EP1_CONFIG = 44102
REG_W2_EP2_CONFIG = 44103
REG_W2_LIMIT_TEMP = 44104
REG_W2_BIVALENCE_TEMP = 44105
REG_W2_BIVALENCE_TEMP_WW = 44106

# ── IO ──
REG_IO_SG_READY_1 = 35101
REG_IO_SG_READY_2 = 35102
REG_IO_OUTPUT_H12 = 35103
REG_IO_OUTPUT_H13 = 35104
REG_IO_OUTPUT_H14 = 35105
REG_IO_OUTPUT_H15 = 35106
REG_IO_INPUT_DE1 = 35107
REG_IO_INPUT_DE2 = 35108
# Holding registers (read-only config)
REG_IO_CFG_SGR1 = 45101
REG_IO_CFG_SGR2 = 45102
REG_IO_CFG_H12 = 45103
REG_IO_CFG_H13 = 45104
REG_IO_CFG_H14 = 45105
REG_IO_CFG_H15 = 45106
REG_IO_CFG_DE1 = 45107
REG_IO_CFG_DE2 = 45108

# ── Statistics (ST) ──
REG_ST_TOTAL_ENERGY_TODAY = 36101
REG_ST_TOTAL_ENERGY_YESTERDAY = 36102
REG_ST_TOTAL_ENERGY_MONTH = 36103
REG_ST_TOTAL_ENERGY_YEAR = 36104
REG_ST_HEATING_ENERGY_TODAY = 36201
REG_ST_HEATING_ENERGY_YESTERDAY = 36202
REG_ST_HEATING_ENERGY_MONTH = 36203
REG_ST_HEATING_ENERGY_YEAR = 36204
REG_ST_HOT_WATER_ENERGY_TODAY = 36301
REG_ST_HOT_WATER_ENERGY_YESTERDAY = 36302
REG_ST_HOT_WATER_ENERGY_MONTH = 36303
REG_ST_HOT_WATER_ENERGY_YEAR = 36304
REG_ST_COOLING_ENERGY_TODAY = 36401
REG_ST_COOLING_ENERGY_YESTERDAY = 36402
REG_ST_COOLING_ENERGY_MONTH = 36403
REG_ST_COOLING_ENERGY_YEAR = 36404
REG_ST_DEFROST_ENERGY_TODAY = 36501
REG_ST_DEFROST_ENERGY_YESTERDAY = 36502
REG_ST_DEFROST_ENERGY_MONTH = 36503
REG_ST_DEFROST_ENERGY_YEAR = 36504
REG_ST_TOTAL2_ENERGY_TODAY = 36601
REG_ST_TOTAL2_ENERGY_YESTERDAY = 36602
REG_ST_TOTAL2_ENERGY_MONTH = 36603
REG_ST_TOTAL2_ENERGY_YEAR = 36604
REG_ST_ELEC_ENERGY_TODAY = 36701
REG_ST_ELEC_ENERGY_YESTERDAY = 36702
REG_ST_ELEC_ENERGY_MONTH = 36703
REG_ST_ELEC_ENERGY_YEAR = 36704


# ──────────────────────────────────────────────────────────
#  Batch read definitions — contiguous register blocks
# ──────────────────────────────────────────────────────────

# (start_address, count) tuples for efficient batch reads
INPUT_REGISTER_BLOCKS: list[tuple[int, int]] = [
    (30001, 6),    # System sensors
    (31101, 6),    # Heating circuit sensors
    (32101, 2),    # Hot water sensors
    (33101, 11),   # Heat pump sensors
    (34101, 7),    # Secondary heater sensors
    (35101, 8),    # IO inputs
    (36101, 4),    # Statistics total
    (36201, 4),    # Statistics heating
    (36301, 4),    # Statistics hot water
    (36401, 4),    # Statistics cooling
    (36501, 4),    # Statistics defrost
    (36601, 4),    # Statistics total II
    (36701, 4),    # Statistics electric
]

HOLDING_REGISTER_BLOCKS: list[tuple[int, int]] = [
    (40001, 2),    # System settings
    (41101, 12),   # Heating circuit settings
    (42101, 5),    # Hot water settings
    (43101, 10),   # Heat pump settings
    (44101, 6),    # Secondary heater settings
    (45101, 8),    # IO config
]
