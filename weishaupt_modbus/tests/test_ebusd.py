"""Tests for ebusd client parsing — field extraction from broadcasts.

Locks in the field-index mapping validated against a real Weishaupt WTC 25-A
on 2026-04-18. If any test here regresses, the HA integration will surface
wrong sensor values in production.
"""

from __future__ import annotations

import asyncio

from weishaupt_modbus.ebusd_client import WeishauptEbusdClient
from weishaupt_modbus.ebusd_const import (
    ALL_FIELDS,
    BROADCASTS,
    CIRCUIT_HC1,
    CIRCUIT_SC,
    HC1_SET_FIELDS,
    SC_ACT_FIELDS,
    EbusdField,
)
from weishaupt_modbus.ebusd_models import (
    EbusdData,
    EbusdDeviceInfo,
    EbusdSensorData,
)


# Live responses captured from a real WTC 25-A on 2026-04-18 — see ebusd_const.py.
SC_ACT_LIVE = (
    "1;BrennerInBetrieb;1;1;1;1;1;1;1;0;0;Summer;0;1;0;0;0;DHW;"
    "42;69.0;26.0;44.0;0.0;21;21.070;8"
)
HC1_SET_LIVE = "hotwater;startconsumer;25.19;-;-;50.0;-"


def _client() -> WeishauptEbusdClient:
    return WeishauptEbusdClient(host="test", port=8888)


# ──────────────────────────────────────────────────────────
# _parse_field — value-type coercion
# ──────────────────────────────────────────────────────────


def test_parse_field_float_rounds_to_two_decimals():
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "float")
    assert client._parse_field("21.070", field) == 21.07


def test_parse_field_float_handles_integer_input():
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "float")
    assert client._parse_field("44", field) == 44.0


def test_parse_field_int_truncates_float_input():
    """ebusd sometimes returns '69.0' for int fields — must coerce via float."""
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "int")
    assert client._parse_field("69.0", field) == 69


def test_parse_field_str_returns_trimmed_string():
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "str")
    assert client._parse_field("  Summer  ", field) == "Summer"


def test_parse_field_dash_sentinel_returns_none():
    """hc1.Set returns '-' for unavailable setpoints."""
    client = _client()
    field = EbusdField("x", CIRCUIT_HC1, "Set", 0, "float")
    assert client._parse_field("-", field) is None


def test_parse_field_empty_value_returns_none():
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "float")
    assert client._parse_field("", field) is None


def test_parse_field_malformed_returns_none():
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 0, "float")
    assert client._parse_field("not-a-number", field) is None


def test_parse_field_out_of_bounds_returns_none():
    """If the broadcast has fewer fields than expected, do not crash."""
    client = _client()
    field = EbusdField("x", CIRCUIT_SC, "Act", 42, "float")
    raw = "one;two;three"
    assert client._parse_field(raw, field) is None


def test_parse_field_extracts_by_index_not_by_name():
    """Fields are positional — selecting by index must pick the right column."""
    client = _client()
    raw = "a;b;c;d"
    assert client._parse_field(raw, EbusdField("x", "sc", "Act", 0, "str")) == "a"
    assert client._parse_field(raw, EbusdField("x", "sc", "Act", 2, "str")) == "c"


# ──────────────────────────────────────────────────────────
# sc.Act — full-broadcast extraction (all 15 mapped fields)
# ──────────────────────────────────────────────────────────


def test_sc_act_operating_phase():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "operating_phase")
    assert client._parse_field(SC_ACT_LIVE, field) == "BrennerInBetrieb"


def test_sc_act_flame_active_is_one():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "flame_active")
    assert client._parse_field(SC_ACT_LIVE, field) == 1


def test_sc_act_gas_valves():
    client = _client()
    gv1 = next(f for f in SC_ACT_FIELDS if f.key == "gas_valve1_active")
    gv2 = next(f for f in SC_ACT_FIELDS if f.key == "gas_valve2_active")
    assert client._parse_field(SC_ACT_LIVE, gv1) == 1
    assert client._parse_field(SC_ACT_LIVE, gv2) == 1


def test_sc_act_pump_active():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "pump_active")
    assert client._parse_field(SC_ACT_LIVE, field) == 1


def test_sc_act_error_inactive():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "error_active")
    assert client._parse_field(SC_ACT_LIVE, field) == 0


def test_sc_act_season():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "season")
    assert client._parse_field(SC_ACT_LIVE, field) == "Summer"


def test_sc_act_operating_mode():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "operating_mode")
    assert client._parse_field(SC_ACT_LIVE, field) == "DHW"


def test_sc_act_load_position():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "load_position")
    assert client._parse_field(SC_ACT_LIVE, field) == 42


def test_sc_act_flow_temp():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "flow_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 69.0


def test_sc_act_exhaust_temp():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "exhaust_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 26.0


def test_sc_act_hot_water_temp():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "hot_water_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 44.0


def test_sc_act_outdoor_temp():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "outdoor_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 21


def test_sc_act_trend_temp_rounded():
    """trend_temp in live capture is 21.070 — must round to 21.07."""
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "trend_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 21.07


def test_sc_act_flow_set_temp():
    client = _client()
    field = next(f for f in SC_ACT_FIELDS if f.key == "flow_set_temp")
    assert client._parse_field(SC_ACT_LIVE, field) == 8


# ──────────────────────────────────────────────────────────
# hc1.Set — full-broadcast extraction
# ──────────────────────────────────────────────────────────


def test_hc1_set_status():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "hc_status")
    assert client._parse_field(HC1_SET_LIVE, field) == "hotwater"


def test_hc1_set_action():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "hc_action")
    assert client._parse_field(HC1_SET_LIVE, field) == "startconsumer"


def test_hc1_set_temp():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "hc_set_temp")
    assert client._parse_field(HC1_SET_LIVE, field) == 25.19


def test_hc1_set_pressure_none_when_dash():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "hc_set_pressure")
    assert client._parse_field(HC1_SET_LIVE, field) is None


def test_hc1_set_output_degree_none_when_dash():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "hc_output_degree")
    assert client._parse_field(HC1_SET_LIVE, field) is None


def test_hc1_set_dhw_set_temp():
    client = _client()
    field = next(f for f in HC1_SET_FIELDS if f.key == "dhw_set_temp")
    assert client._parse_field(HC1_SET_LIVE, field) == 50.0


# ──────────────────────────────────────────────────────────
# Field-map invariants — guard against accidental edits to ebusd_const
# ──────────────────────────────────────────────────────────


def test_sc_act_field_count():
    """15 fields mapped from sc.Act. Update this test if the map grows."""
    assert len(SC_ACT_FIELDS) == 15


def test_hc1_set_field_count():
    assert len(HC1_SET_FIELDS) == 6


def test_all_fields_is_union():
    assert ALL_FIELDS == SC_ACT_FIELDS + HC1_SET_FIELDS


def test_broadcasts_cover_every_field():
    """Every field must belong to a (circuit, message) in BROADCASTS,
    otherwise async_read_all would never fetch its source."""
    broadcast_set = set(BROADCASTS)
    for field in ALL_FIELDS:
        assert (field.circuit, field.message) in broadcast_set


def test_field_keys_are_unique():
    """Two fields with the same key would overwrite each other in values dict."""
    keys = [f.key for f in ALL_FIELDS]
    assert len(keys) == len(set(keys))


def test_field_indices_unique_per_broadcast():
    """Within one broadcast, reading the same index twice is a copy-paste bug."""
    for circuit, message in BROADCASTS:
        indices = [
            f.field_index for f in ALL_FIELDS
            if f.circuit == circuit and f.message == message
        ]
        assert len(indices) == len(set(indices)), (
            f"Duplicate field_index in {circuit}.{message}"
        )


# ──────────────────────────────────────────────────────────
# Data-model defaults
# ──────────────────────────────────────────────────────────


def test_ebusd_sensor_data_defaults_to_none():
    """None signals 'not available' — HA entities rely on this."""
    sensors = EbusdSensorData()
    assert sensors.outdoor_temp is None
    assert sensors.flow_temp is None
    assert sensors.flame_active is None
    assert sensors.gas_valve1_active is None
    assert sensors.gas_valve2_active is None


def test_ebusd_device_info_defaults():
    info = EbusdDeviceInfo()
    assert info.ebusd_version == "unknown"
    assert info.device_name == "Weishaupt WTC"


def test_ebusd_data_composes_nested_dataclasses():
    data = EbusdData()
    assert isinstance(data.sensors, EbusdSensorData)
    assert isinstance(data.device_info, EbusdDeviceInfo)
    assert data.raw_values == {}


# ──────────────────────────────────────────────────────────
# async_read_all — end-to-end with a fake ebusd connection
# ──────────────────────────────────────────────────────────


class _FakeWriter:
    """Minimal asyncio.StreamWriter stand-in for testing the client."""

    def __init__(self) -> None:
        self.written: list[bytes] = []
        self._closing = False

    def write(self, data: bytes) -> None:
        self.written.append(data)

    async def drain(self) -> None:
        return None

    def is_closing(self) -> bool:
        return self._closing

    def close(self) -> None:
        self._closing = True

    async def wait_closed(self) -> None:
        return None


def _make_client_with_responses(*responses: str) -> tuple[WeishauptEbusdClient, _FakeWriter]:
    """Build a client wired to a StreamReader pre-loaded with the given
    newline-terminated responses, in the order they will be read."""
    reader = asyncio.StreamReader()
    for resp in responses:
        reader.feed_data(resp.encode() + b"\n")
    reader.feed_eof()

    writer = _FakeWriter()
    client = WeishauptEbusdClient(host="fake", port=8888)
    client._reader = reader
    client._writer = writer  # type: ignore[assignment]
    return client, writer


async def test_async_read_all_happy_path_extracts_all_fields():
    """With live broadcasts queued in BROADCASTS order, every mapped field
    must land in EbusdData with the expected typed value."""
    client, writer = _make_client_with_responses(SC_ACT_LIVE, HC1_SET_LIVE)

    data = await client.async_read_all()

    # sc.Act-derived fields
    assert data.sensors.operating_phase == "BrennerInBetrieb"
    assert data.sensors.flame_active == 1
    assert data.sensors.gas_valve1_active == 1
    assert data.sensors.gas_valve2_active == 1
    assert data.sensors.pump_active == 1
    assert data.sensors.error_active == 0
    assert data.sensors.season == "Summer"
    assert data.sensors.operating_mode == "DHW"
    assert data.sensors.load_position == 42
    assert data.sensors.flow_temp == 69.0
    assert data.sensors.exhaust_temp == 26.0
    assert data.sensors.hot_water_temp == 44.0
    assert data.sensors.outdoor_temp == 21
    assert data.sensors.trend_temp == 21.07
    assert data.sensors.flow_set_temp == 8

    # hc1.Set-derived fields
    assert data.sensors.hc_status == "hotwater"
    assert data.sensors.dhw_set_temp == 50.0

    # Commands issued in the expected order — one per broadcast.
    assert writer.written == [b"read -c sc Act\n", b"read -c hc1 Set\n"]

    # raw_values exposes only non-None entries for dashboards/diagnostics.
    assert "flow_temp" in data.raw_values
    assert "hc_set_pressure" not in data.raw_values  # live response has '-'


async def test_async_read_all_error_response_yields_none_fields():
    """ebusd returns 'ERR: ...' when a broadcast is not cached. Every field
    that belongs to that broadcast must come back as None — no exception."""
    client, _ = _make_client_with_responses(
        "ERR: message not defined",  # sc.Act unavailable
        HC1_SET_LIVE,
    )

    data = await client.async_read_all()

    # All sc.Act-sourced attributes are None.
    assert data.sensors.flow_temp is None
    assert data.sensors.outdoor_temp is None
    assert data.sensors.season is None
    assert data.sensors.gas_valve1_active is None

    # hc1.Set-sourced attributes are still populated.
    assert data.sensors.hc_status == "hotwater"
    assert data.sensors.dhw_set_temp == 50.0


async def test_async_read_all_both_broadcasts_error():
    """Full outage: both broadcasts return ERR — no crash, all None."""
    client, _ = _make_client_with_responses(
        "ERR: no signal",
        "ERR: no signal",
    )

    data = await client.async_read_all()

    assert data.sensors.flow_temp is None
    assert data.sensors.hc_status is None
    assert data.raw_values == {}
