"""Async HTTP client for Weishaupt WCM-COM module (coco protocol).

Communicates with WCM-COM modules that provide an HTTP API on gas boilers
(WTC series) and potentially other Weishaupt heating devices connected via eBUS.

Protocol: POST /parameter.json with JSON body containing "coco" telegrams.
Authentication: HTTP Digest Auth.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from .exceptions import (
    WeishauptConnectionError,
    WeishauptReadError,
    WeishauptWriteError,
)
from .wcm_const import (
    CMD_READ,
    CMD_WRITE,
    COCO_PROTOCOL,
    DEFAULT_HTTP_PORT,
    DEFAULT_TIMEOUT,
    DEVICE_INFO_PARAMS,
    MAX_TELEGRAMS_PER_REQUEST,
    SENSOR_PARAMS,
    STATS_PARAMS,
    VALUE_NOT_AVAILABLE,
    ParamDef,
)
from .wcm_models import (
    WCMData,
    WCMDeviceInfo,
    WTCSensorData,
    WTCStatisticsData,
)

_LOGGER = logging.getLogger(__name__)


def _decode_value(low: int, high: int, param: ParamDef) -> float | None:
    """Decode a coco telegram value from low/high bytes.

    Returns None if the value is the "not available" sentinel (0x8000).
    """
    # Check for N/V sentinel
    if low == 0 and high == 128:  # 0x8000
        return None

    # Reconstruct 16-bit signed value
    if param.signed:
        if high <= 127:
            raw = high * 256 + low
        elif high == 128 and low == 0:
            return None  # Also N/V
        else:
            raw = -32768 + (high - 128) * 256 + low
    else:
        raw = high * 256 + low

    # Apply scale
    if param.scale > 1:
        return round(raw / param.scale, 1)
    return float(raw)


def _build_telegram(param: ParamDef, command: int = CMD_READ,
                    value: int = 0) -> list[int]:
    """Build a single coco telegram array."""
    lo = value & 0xFF
    hi = (value >> 8) & 0xFF
    return [param.module_type, 0, command, param.infonr, 0, 0, lo, hi]


class WeishauptWCMClient:
    """Async HTTP client for WCM-COM module using coco protocol."""

    def __init__(
        self,
        host: str,
        username: str = "admin",
        password: str = "",
        port: int = DEFAULT_HTTP_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the WCM-COM HTTP client."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()
        self._base_url = f"http://{host}:{port}" if port != 80 else f"http://{host}"

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    @property
    def connected(self) -> bool:
        """Return True if client exists."""
        return self._client is not None and not self._client.is_closed

    async def connect(self) -> None:
        """Create the HTTP client with Digest Auth."""
        if self.connected:
            return
        self._client = httpx.AsyncClient(
            auth=httpx.DigestAuth(self._username, self._password),
            timeout=httpx.Timeout(self._timeout),
        )
        _LOGGER.debug("WCM-COM HTTP client created for %s", self._base_url)

    async def disconnect(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            _LOGGER.debug("WCM-COM HTTP client closed")

    async def _request(
        self, telegrams: list[list[int]]
    ) -> list[list[Any]]:
        """Send a coco protocol request and return the response telegrams.

        Handles batching if more than MAX_TELEGRAMS_PER_REQUEST telegrams.
        """
        if not self._client or self._client.is_closed:
            await self.connect()
        assert self._client is not None

        url = f"{self._base_url}/parameter.json"
        all_responses: list[list[Any]] = []

        # Batch telegrams
        for i in range(0, len(telegrams), MAX_TELEGRAMS_PER_REQUEST):
            batch = telegrams[i : i + MAX_TELEGRAMS_PER_REQUEST]
            payload = {"prot": COCO_PROTOCOL, "telegramm": batch}

            try:
                resp = await self._client.post(url, json=payload)

                if resp.status_code == 401:
                    raise WeishauptConnectionError(
                        "Authentication failed. Check username/password."
                    )
                if resp.status_code != 200:
                    raise WeishauptReadError(
                        f"HTTP {resp.status_code} from WCM-COM"
                    )
                data = resp.json()
                all_responses.extend(data.get("telegramm", []))

            except httpx.HTTPError as err:
                raise WeishauptConnectionError(
                    f"Cannot connect to WCM-COM at {self._base_url}: {err}"
                ) from err

        return all_responses

    async def async_read_params(
        self, params: list[ParamDef]
    ) -> dict[int, float | str | None]:
        """Read a list of parameters and return {infonr: decoded_value}."""
        telegrams = [_build_telegram(p) for p in params]

        async with self._lock:
            responses = await self._request(telegrams)

        result: dict[int, float | str | None] = {}
        for resp in responses:
            if len(resp) < 7:
                continue

            infonr = resp[3]

            # String response (some system params return strings)
            if isinstance(resp[6], str):
                result[infonr] = resp[6]
                continue

            if len(resp) < 8:
                continue

            # Find the param definition for this infonr
            param = next((p for p in params if p.infonr == infonr), None)
            if param is None:
                continue

            low = resp[6]
            high = resp[7]
            result[infonr] = _decode_value(low, high, param)

        return result

    async def async_write_param(self, param: ParamDef, value: int) -> None:
        """Write a value to a parameter."""
        telegram = _build_telegram(param, command=CMD_WRITE, value=value)

        async with self._lock:
            responses = await self._request([telegram])

        # Check for error response
        for resp in responses:
            if len(resp) >= 3 and resp[2] == 255:  # CMD_ERROR
                raise WeishauptWriteError(
                    f"WCM-COM rejected write to INFONR {param.infonr}"
                )

    async def async_identify_device(self) -> WCMDeviceInfo:
        """Read device identification from WCM-COM."""
        await self.connect()
        values = await self.async_read_params(DEVICE_INFO_PARAMS)

        return WCMDeviceInfo(
            device_name=str(values.get(5066, "Weishaupt WTC")),
            device_type_id=int(values.get(5067, 0) or 0),
            hostname=str(values.get(5090, "wcm-com")),
            firmware_version=int(values.get(5010, 0) or 0),
            serial_number=f"wcm_{self._host}",
        )

    async def async_read_all(self) -> WCMData:
        """Read all sensor data and return a complete snapshot."""
        # Read sensors and stats in one combined request
        all_params = SENSOR_PARAMS + STATS_PARAMS
        values = await self.async_read_params(all_params)

        sensors = WTCSensorData(
            outdoor_temp=values.get(12),
            damped_outdoor_temp=values.get(2572),
            flow_temp=values.get(13),
            return_temp=values.get(3101),
            hot_water_temp=values.get(14),
            exhaust_temp=values.get(325),
            buffer_top_temp=values.get(118),
            buffer_bottom_temp=values.get(120),
            heat_request=values.get(2),
            load_position=int(values.get(138, 0) or 0) if values.get(138) is not None else None,
            load_setting_kw=values.get(4176),
            flow_rate=values.get(130),
            operating_phase=int(values.get(373, 0) or 0) if values.get(373) is not None else None,
            error_code=int(values.get(1, 0) or 0),
        )

        # Oil meter is combined from high (×1000) and low parts
        oil_high = int(values.get(3792, 0) or 0)
        oil_low = int(values.get(3793, 0) or 0)
        oil_total = oil_high * 1000 + oil_low

        statistics = WTCStatisticsData(
            burner_hours=int(values.get(3198, 0) or 0),
            burner_cycles=int(values.get(3196, 0) or 0),
            oil_meter=float(oil_total),
        )

        return WCMData(
            sensors=sensors,
            statistics=statistics,
            raw_values={k: v for k, v in values.items() if v is not None},
        )

    async def async_test_connection(self) -> bool:
        """Test if the WCM-COM module is reachable and responsive."""
        try:
            await self.connect()
            from .wcm_const import PARAM_ERROR_CODE
            values = await self.async_read_params([PARAM_ERROR_CODE])
            return 1 in values  # INFONR 1 (error code) should be present
        except (WeishauptConnectionError, WeishauptReadError):
            return False
