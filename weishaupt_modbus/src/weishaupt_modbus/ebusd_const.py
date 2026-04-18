"""Constants and message definitions for ebusd communication.

Validated against real Weishaupt WTC 25-A hardware (2026-04-18) via
eBUS Adapter Shield C6 on WLAN + ebusd 26.1 + J0EK3R CSV configuration.

The WTC exposes its live values through two broadcast messages that ebusd
caches automatically:

    sc.Act  — System Controller broadcast (TrendTemp, SupplyTemp, DHWTemp,
              ExternalTemp, Load, Flame, Pump, Error, Operatingphase, ...)
    hc1.Set — Heating Circuit 1 setpoints (DHWSetTemp, SetTemp, Status, ...)

We read each broadcast once and extract fields by index, rather than polling
individual sensor messages (which don't exist for this model).
"""

from __future__ import annotations

from dataclasses import dataclass

# Connection defaults
DEFAULT_EBUSD_PORT = 8888
DEFAULT_EBUSD_TIMEOUT = 10

# Circuits discovered during scan (Weishaupt WTC 25-A with SC and one HC)
CIRCUIT_SC = "sc"
CIRCUIT_HC1 = "hc1"


@dataclass(frozen=True)
class EbusdField:
    """A single field within an ebusd multi-field message."""

    key: str                # Internal key (matches EbusdSensorData attribute)
    circuit: str            # ebusd circuit (e.g. "sc", "hc1")
    message: str            # ebusd message name (e.g. "Act", "Set")
    field_index: int        # 0-based field position in the response
    value_type: str = "float"  # "float", "int", or "str"


# ──────────────────────────────────────────────────────────
#  sc.Act — System Controller broadcast (27 fields)
#
#  Live example response:
#  1;BrennerInBetrieb;1;1;1;1;1;1;1;0;0;Summer;0;1;0;0;0;DHW;42;69.0;26.0;44.0;0.0;21;21.070;8
#  │ └operating_phase  └flame (5)          └season(11)  └mode(17) │  └supply  │    └hotwater  │   └outdoor  │      └flow_set(25)
#                                                                 load(18)   exhaust(20)    unknown(22)   trend(24)
# ──────────────────────────────────────────────────────────

SC_ACT_FIELDS: list[EbusdField] = [
    EbusdField("operating_phase", CIRCUIT_SC, "Act", 1, "str"),
    EbusdField("flame_active", CIRCUIT_SC, "Act", 5, "int"),
    EbusdField("gas_valve1_active", CIRCUIT_SC, "Act", 6, "int"),
    EbusdField("gas_valve2_active", CIRCUIT_SC, "Act", 7, "int"),
    EbusdField("pump_active", CIRCUIT_SC, "Act", 8, "int"),
    EbusdField("error_active", CIRCUIT_SC, "Act", 9, "int"),
    EbusdField("season", CIRCUIT_SC, "Act", 11, "str"),
    EbusdField("operating_mode", CIRCUIT_SC, "Act", 17, "str"),
    EbusdField("load_position", CIRCUIT_SC, "Act", 18, "int"),
    EbusdField("flow_temp", CIRCUIT_SC, "Act", 19, "float"),
    EbusdField("exhaust_temp", CIRCUIT_SC, "Act", 20, "float"),
    EbusdField("hot_water_temp", CIRCUIT_SC, "Act", 21, "float"),
    EbusdField("outdoor_temp", CIRCUIT_SC, "Act", 23, "int"),
    EbusdField("trend_temp", CIRCUIT_SC, "Act", 24, "float"),
    EbusdField("flow_set_temp", CIRCUIT_SC, "Act", 25, "int"),
]

# ──────────────────────────────────────────────────────────
#  hc1.Set — Heating Circuit 1 setpoints broadcast (7 fields)
#
#  Live example response:
#  hotwater;startconsumer;25.19;-;-;50.0;-
#  └status  └action       │     │ │ └dhw_set_temp
#                         set_temp(2)  output(4)
# ──────────────────────────────────────────────────────────

HC1_SET_FIELDS: list[EbusdField] = [
    EbusdField("hc_status", CIRCUIT_HC1, "Set", 0, "str"),
    EbusdField("hc_action", CIRCUIT_HC1, "Set", 1, "str"),
    EbusdField("hc_set_temp", CIRCUIT_HC1, "Set", 2, "float"),
    EbusdField("hc_set_pressure", CIRCUIT_HC1, "Set", 3, "float"),
    EbusdField("hc_output_degree", CIRCUIT_HC1, "Set", 4, "float"),
    EbusdField("dhw_set_temp", CIRCUIT_HC1, "Set", 5, "float"),
]

# All fields combined, used by the client for a full read cycle.
ALL_FIELDS: list[EbusdField] = SC_ACT_FIELDS + HC1_SET_FIELDS

# Grouped per (circuit, message) so we can read each broadcast exactly once.
BROADCASTS: list[tuple[str, str]] = [
    (CIRCUIT_SC, "Act"),
    (CIRCUIT_HC1, "Set"),
]
