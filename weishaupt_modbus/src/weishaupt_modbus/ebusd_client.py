"""Async TCP client for ebusd daemon communication.

Communicates with ebusd via its TCP telnet interface (default port 8888).
Used with eBUS Adapter Shield/Stick hardware connected to Weishaupt WTC
gas boilers.

Data acquisition strategy: the WTC emits two broadcast messages (sc.Act
and hc1.Set) which ebusd caches. We read each broadcast once per cycle
and extract individual sensor values by field index.
"""

from __future__ import annotations

import asyncio
import logging

from .ebusd_const import (
    ALL_FIELDS,
    BROADCASTS,
    DEFAULT_EBUSD_PORT,
    DEFAULT_EBUSD_TIMEOUT,
    EBUSD_SETTINGS,
    EbusdField,
)
from .ebusd_models import EbusdData, EbusdDeviceInfo, EbusdSensorData
from .exceptions import (
    WeishauptConnectionError,
    WeishauptReadError,
    WeishauptWriteError,
)

_LOGGER = logging.getLogger(__name__)


class WeishauptEbusdClient:
    """Async TCP client for ebusd daemon."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = DEFAULT_EBUSD_PORT,
        timeout: int = DEFAULT_EBUSD_TIMEOUT,
        circuit: str = "",
    ) -> None:
        """Initialize the ebusd TCP client."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self._circuit = circuit
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    @property
    def connected(self) -> bool:
        """Return True if connected to ebusd."""
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        """Open TCP connection to ebusd."""
        if self.connected:
            return
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._timeout,
            )
            _LOGGER.debug("Connected to ebusd at %s:%d", self._host, self._port)
        except (OSError, asyncio.TimeoutError) as err:
            raise WeishauptConnectionError(
                f"Cannot connect to ebusd at {self._host}:{self._port}: {err}"
            ) from err

    async def disconnect(self) -> None:
        """Close TCP connection."""
        if self._writer and not self._writer.is_closing():
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
            self._writer = None
            self._reader = None
            _LOGGER.debug("Disconnected from ebusd")

    async def _send_command(self, command: str) -> str:
        """Send a command to ebusd and return the full response.

        ebusd terminates each response with a blank line. We read until we
        see it, otherwise multi-line replies (e.g. `info`) leave the tail
        in the socket buffer and the next command picks it up as its
        result — that has happened: `info` output "max symbol rate: 64"
        was consumed as the hc1.Set response.
        """
        if not self.connected:
            await self.connect()
        assert self._reader is not None
        assert self._writer is not None

        try:
            self._writer.write(f"{command}\n".encode())
            await self._writer.drain()

            lines: list[str] = []
            while True:
                raw = await asyncio.wait_for(
                    self._reader.readline(),
                    timeout=self._timeout,
                )
                line = raw.decode().rstrip("\r\n")
                if not line:
                    break
                lines.append(line)
            return "\n".join(lines)
        except (OSError, asyncio.TimeoutError) as err:
            self._writer = None
            self._reader = None
            raise WeishauptConnectionError(
                f"ebusd communication error: {err}"
            ) from err

    async def _read_single_value(self, circuit: str, message: str) -> float | None:
        """Read an active (non-broadcast) message and parse as float.

        Used for user-level setpoints exposed via `ebusctl read -c <c> <m>`.
        ebusd caches these between polls so repeated calls stay cheap.
        """
        cmd = f"read -c {circuit} {message}"
        async with self._lock:
            response = await self._send_command(cmd)

        if not response or response.startswith("ERR:"):
            return None
        first_line = response.split("\n", 1)[0].strip()
        try:
            return float(first_line)
        except ValueError:
            _LOGGER.debug(
                "ebusd %s.%s: cannot parse %r as float",
                circuit,
                message,
                first_line,
            )
            return None

    async def _read_broadcast(self, circuit: str, message: str) -> str | None:
        """Read a cached broadcast message. Returns raw response or None."""
        cmd = f"read -c {circuit} {message}"
        async with self._lock:
            response = await self._send_command(cmd)

        if not response or response.startswith("ERR:"):
            _LOGGER.debug("ebusd %s.%s: %s", circuit, message, response)
            return None
        # `read` always returns a single value line, but _send_command may
        # return a multi-line string if ebusd ever appends extras — keep
        # only the first line to stay robust.
        return response.split("\n", 1)[0]

    def _parse_field(self, raw: str, field: EbusdField) -> float | int | str | None:
        """Extract one field from a semicolon-separated ebusd response."""
        parts = raw.split(";")
        if field.field_index >= len(parts):
            return None

        value_str = parts[field.field_index].strip()
        if not value_str or value_str == "-":
            return None

        try:
            if field.value_type == "float":
                return round(float(value_str), 2)
            if field.value_type == "int":
                return int(float(value_str))
            return value_str
        except (ValueError, TypeError):
            _LOGGER.debug("Cannot parse '%s' for %s", value_str, field.key)
            return None

    async def async_get_info(self) -> dict[str, str]:
        """Get ebusd daemon info (version, signal, device)."""
        async with self._lock:
            response = await self._send_command("info")

        result: dict[str, str] = {}
        for line in response.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip().lower()] = val.strip()
        return result

    async def async_get_state(self) -> str:
        """Get ebusd signal/connection state."""
        async with self._lock:
            return await self._send_command("state")

    async def async_identify_device(self) -> EbusdDeviceInfo:
        """Read device identification via ebusd info command."""
        await self.connect()
        info = await self.async_get_info()

        return EbusdDeviceInfo(
            ebusd_version=info.get("version", "unknown"),
            device_name="Weishaupt WTC",
            signal_state=info.get("signal", "unknown"),
            serial_number=f"ebusd_{self._host}",
        )

    async def async_read_all(self) -> EbusdData:
        """Read both broadcasts and extract all sensor fields."""
        # Read each broadcast once, cache the raw responses by (circuit, message).
        raw_responses: dict[tuple[str, str], str | None] = {}
        for circuit, message in BROADCASTS:
            raw_responses[(circuit, message)] = await self._read_broadcast(
                circuit, message
            )

        # Build the flat key→value dictionary by extracting each field.
        values: dict[str, float | int | str | None] = {}
        for field in ALL_FIELDS:
            raw = raw_responses.get((field.circuit, field.message))
            values[field.key] = self._parse_field(raw, field) if raw else None

        sensors = EbusdSensorData(
            outdoor_temp=values.get("outdoor_temp"),
            flow_temp=values.get("flow_temp"),
            flow_set_temp=values.get("flow_set_temp"),
            hot_water_temp=values.get("hot_water_temp"),
            dhw_set_temp=values.get("dhw_set_temp"),
            exhaust_temp=values.get("exhaust_temp"),
            trend_temp=values.get("trend_temp"),
            load_position=values.get("load_position"),
            operating_phase=values.get("operating_phase"),
            season=values.get("season"),
            operating_mode=values.get("operating_mode"),
            hc_status=values.get("hc_status"),
            flame_active=values.get("flame_active"),
            pump_active=values.get("pump_active"),
            error_active=values.get("error_active"),
            gas_valve1_active=values.get("gas_valve1_active"),
            gas_valve2_active=values.get("gas_valve2_active"),
        )

        # Active reads for editable setpoints. ebusd returns None for each
        # setting whose message isn't loaded — that's the case on installs
        # still running with --scanconfig. The integration degrades
        # gracefully: the number entities go to Unknown.
        for attr, circuit, message in EBUSD_SETTINGS:
            try:
                val = await self._read_single_value(circuit, message)
            except WeishauptConnectionError:
                val = None
            setattr(sensors, attr, val)
            if val is not None:
                values[attr] = val

        return EbusdData(
            sensors=sensors,
            raw_values={k: v for k, v in values.items() if v is not None},
        )

    async def async_write_field(
        self, circuit: str, message: str, value: float | int | str
    ) -> None:
        """Write a value to an ebusd message.

        Equivalent to `ebusctl write -c <circuit> <message> <value>`.
        ebusd answers "done" on success and "ERR: ..." on failure.
        """
        cmd = f"write -c {circuit} {message} {value}"
        async with self._lock:
            response = await self._send_command(cmd)

        if not response:
            raise WeishauptWriteError(
                f"empty response from ebusd when writing {circuit}.{message}"
            )
        if response.startswith("ERR:"):
            raise WeishauptWriteError(
                f"ebusd rejected write to {circuit}.{message}: {response}"
            )
        if response.strip().lower() != "done":
            _LOGGER.warning(
                "unexpected write response from %s.%s: %r",
                circuit,
                message,
                response,
            )

    async def async_test_connection(self) -> bool:
        """Test if ebusd is reachable and has signal."""
        try:
            await self.connect()
            state = await self.async_get_state()
            return "signal acquired" in state.lower() or "acquired" in state.lower()
        except (WeishauptConnectionError, WeishauptReadError):
            return False
