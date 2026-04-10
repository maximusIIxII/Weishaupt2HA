"""Async Modbus TCP client for Weishaupt heat pumps via WCM-COM."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    HOLDING_REGISTER_BLOCKS,
    INPUT_REGISTER_BLOCKS,
    TEMPERATURE_SCALE,
    # System registers
    REG_SYS_OUTDOOR_TEMP,
    REG_SYS_AIR_INTAKE_TEMP,
    REG_SYS_ERROR,
    REG_SYS_WARNING,
    REG_SYS_ERROR_FREE,
    REG_SYS_DISPLAY_STATUS,
    REG_SYS_OPERATION_MODE,
    REG_SYS_PV_SETPOINT,
    # Heat pump registers
    REG_HP_OPERATION_STATUS,
    REG_HP_ERROR_STATUS,
    REG_HP_POWER_REQUEST,
    REG_HP_FLOW_TEMP,
    REG_HP_RETURN_TEMP,
    REG_HP_EVAPORATOR_TEMP,
    REG_HP_COMPRESSOR_INTAKE_TEMP,
    REG_HP_SWITCH_TEMP,
    REG_HP_REQUEST_REGEN,
    REG_HP_BUFFER_TEMP,
    REG_HP_PRECISE_FLOW_TEMP,
    REG_HP_CONFIG,
    REG_HP_QUIET_MODE,
    REG_HP_PUMP_START_MODE,
    REG_HP_PUMP_POWER_HEATING,
    REG_HP_PUMP_POWER_COOLING,
    REG_HP_PUMP_POWER_HOT_WATER,
    REG_HP_PUMP_POWER_DEFROST,
    REG_HP_FLOW_RATE_HEATING,
    REG_HP_FLOW_RATE_COOLING,
    REG_HP_FLOW_RATE_HOT_WATER,
    # Hot water registers
    REG_WW_TARGET_TEMP,
    REG_WW_CURRENT_TEMP,
    REG_WW_CONFIG,
    REG_WW_PUSH,
    REG_WW_NORMAL_TEMP,
    REG_WW_REDUCED_TEMP,
    REG_WW_SG_READY_BOOST,
    # Heating circuit registers
    REG_HZ_ROOM_TARGET_TEMP,
    REG_HZ_ROOM_TEMP,
    REG_HZ_ROOM_HUMIDITY,
    REG_HZ_FLOW_TARGET_TEMP,
    REG_HZ_FLOW_TEMP,
    REG_HZ_CONFIG,
    REG_HZ_REQUEST_TYPE,
    REG_HZ_OPERATION_MODE,
    REG_HZ_PARTY_PAUSE,
    REG_HZ_COMFORT_TEMP,
    REG_HZ_NORMAL_TEMP,
    REG_HZ_REDUCED_TEMP,
    REG_HZ_HEATING_CURVE,
    REG_HZ_SUMMER_WINTER_SWITCH,
    REG_HZ_CONST_TEMP_HEATING,
    REG_HZ_CONST_TEMP_REDUCED,
    REG_HZ_CONST_TEMP_COOLING,
    # Secondary heater registers
    REG_W2_STATUS,
    REG_W2_EHEATER1_CYCLES,
    REG_W2_EHEATER1_HOURS,
    REG_W2_EHEATER1_STATUS,
    REG_W2_EHEATER2_STATUS,
    REG_W2_EHEATER2_CYCLES,
    REG_W2_EHEATER2_HOURS,
    REG_W2_CONFIG,
    REG_W2_EP1_CONFIG,
    REG_W2_EP2_CONFIG,
    REG_W2_LIMIT_TEMP,
    REG_W2_BIVALENCE_TEMP,
    REG_W2_BIVALENCE_TEMP_WW,
    # Statistics registers
    REG_ST_TOTAL_ENERGY_TODAY,
    REG_ST_TOTAL_ENERGY_YESTERDAY,
    REG_ST_TOTAL_ENERGY_MONTH,
    REG_ST_TOTAL_ENERGY_YEAR,
    REG_ST_HEATING_ENERGY_TODAY,
    REG_ST_HEATING_ENERGY_YESTERDAY,
    REG_ST_HEATING_ENERGY_MONTH,
    REG_ST_HEATING_ENERGY_YEAR,
    REG_ST_HOT_WATER_ENERGY_TODAY,
    REG_ST_HOT_WATER_ENERGY_YESTERDAY,
    REG_ST_HOT_WATER_ENERGY_MONTH,
    REG_ST_HOT_WATER_ENERGY_YEAR,
    REG_ST_COOLING_ENERGY_TODAY,
    REG_ST_COOLING_ENERGY_YESTERDAY,
    REG_ST_COOLING_ENERGY_MONTH,
    REG_ST_COOLING_ENERGY_YEAR,
    REG_ST_DEFROST_ENERGY_TODAY,
    REG_ST_DEFROST_ENERGY_YESTERDAY,
    REG_ST_DEFROST_ENERGY_MONTH,
    REG_ST_DEFROST_ENERGY_YEAR,
    REG_ST_TOTAL2_ENERGY_TODAY,
    REG_ST_TOTAL2_ENERGY_YESTERDAY,
    REG_ST_TOTAL2_ENERGY_MONTH,
    REG_ST_TOTAL2_ENERGY_YEAR,
    REG_ST_ELEC_ENERGY_TODAY,
    REG_ST_ELEC_ENERGY_YESTERDAY,
    REG_ST_ELEC_ENERGY_MONTH,
    REG_ST_ELEC_ENERGY_YEAR,
)
from .exceptions import (
    WeishauptConnectionError,
    WeishauptReadError,
    WeishauptWriteError,
)
from .models import (
    DeviceInfo,
    EnergyBlock,
    HeatingCircuitData,
    HeatPumpData,
    HotWaterData,
    SecondaryHeaterData,
    StatisticsData,
    SystemData,
    WeishauptData,
)

_LOGGER = logging.getLogger(__name__)


def _signed(value: int) -> int:
    """Convert unsigned 16-bit to signed 16-bit."""
    return value - 65536 if value >= 32768 else value


def _temp(value: int) -> float | None:
    """Convert raw register to temperature (°C). Returns None for invalid values."""
    signed = _signed(value)
    if signed == -32768 or signed == 32767:
        return None
    return round(signed * TEMPERATURE_SCALE, 1)


def _energy(value: int) -> float:
    """Convert raw register to energy (kWh)."""
    return round(value * TEMPERATURE_SCALE, 1)


class WeishauptModbusClient:
    """Async Modbus TCP client for Weishaupt WCM-COM module."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        slave_id: int = DEFAULT_SLAVE_ID,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._timeout = timeout
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    @property
    def connected(self) -> bool:
        """Return True if connected."""
        return self._client is not None and self._client.connected

    async def connect(self) -> None:
        """Connect to the WCM-COM module."""
        if self.connected:
            return
        try:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=self._timeout,
            )
            connected = await self._client.connect()
            if not connected:
                raise WeishauptConnectionError(
                    f"Could not connect to {self._host}:{self._port}"
                )
            _LOGGER.debug("Connected to Weishaupt WCM-COM at %s:%s", self._host, self._port)
        except ModbusException as err:
            raise WeishauptConnectionError(
                f"Modbus connection failed: {err}"
            ) from err

    async def disconnect(self) -> None:
        """Disconnect from the WCM-COM module."""
        if self._client:
            self._client.close()
            self._client = None
            _LOGGER.debug("Disconnected from Weishaupt WCM-COM")

    async def _read_input_registers(self, address: int, count: int) -> list[int]:
        """Read input registers (read-only values)."""
        if not self._client or not self._client.connected:
            await self.connect()
        assert self._client is not None
        try:
            result = await self._client.read_input_registers(
                address=address, count=count, slave=self._slave_id
            )
            if result.isError():
                raise WeishauptReadError(f"Error reading input registers at {address}: {result}")
            return list(result.registers)
        except ModbusException as err:
            raise WeishauptReadError(f"Failed to read input registers at {address}: {err}") from err

    async def _read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read holding registers (settings/config)."""
        if not self._client or not self._client.connected:
            await self.connect()
        assert self._client is not None
        try:
            result = await self._client.read_holding_registers(
                address=address, count=count, slave=self._slave_id
            )
            if result.isError():
                raise WeishauptReadError(f"Error reading holding registers at {address}: {result}")
            return list(result.registers)
        except ModbusException as err:
            raise WeishauptReadError(
                f"Failed to read holding registers at {address}: {err}"
            ) from err

    async def async_write_register(self, address: int, value: int) -> None:
        """Write a single holding register."""
        if not self._client or not self._client.connected:
            await self.connect()
        assert self._client is not None
        async with self._lock:
            try:
                result = await self._client.write_register(
                    address=address, value=value, slave=self._slave_id
                )
                if result.isError():
                    raise WeishauptWriteError(
                        f"Error writing register {address}={value}: {result}"
                    )
                _LOGGER.debug("Wrote register %d = %d", address, value)
            except ModbusException as err:
                raise WeishauptWriteError(
                    f"Failed to write register {address}: {err}"
                ) from err

    async def _read_all_input_registers(self) -> dict[int, int]:
        """Read all input register blocks and return address->value map."""
        registers: dict[int, int] = {}
        for start_addr, count in INPUT_REGISTER_BLOCKS:
            try:
                values = await self._read_input_registers(start_addr, count)
                for i, val in enumerate(values):
                    registers[start_addr + i] = val
            except WeishauptReadError:
                _LOGGER.warning("Failed to read input register block at %d", start_addr)
        return registers

    async def _read_all_holding_registers(self) -> dict[int, int]:
        """Read all holding register blocks and return address->value map."""
        registers: dict[int, int] = {}
        for start_addr, count in HOLDING_REGISTER_BLOCKS:
            try:
                values = await self._read_holding_registers(start_addr, count)
                for i, val in enumerate(values):
                    registers[start_addr + i] = val
            except WeishauptReadError:
                _LOGGER.warning("Failed to read holding register block at %d", start_addr)
        return registers

    def _parse_system(self, inp: dict[int, int], hold: dict[int, int]) -> SystemData:
        """Parse system data from registers."""
        return SystemData(
            outdoor_temp=_temp(inp[REG_SYS_OUTDOOR_TEMP]) if REG_SYS_OUTDOOR_TEMP in inp else None,
            air_intake_temp=_temp(inp[REG_SYS_AIR_INTAKE_TEMP]) if REG_SYS_AIR_INTAKE_TEMP in inp else None,
            error_code=inp.get(REG_SYS_ERROR, 65535),
            warning_code=inp.get(REG_SYS_WARNING, 65535),
            error_free=inp.get(REG_SYS_ERROR_FREE, 0),
            display_status=inp.get(REG_SYS_DISPLAY_STATUS, 0),
            operation_mode=hold.get(REG_SYS_OPERATION_MODE, 0),
            pv_setpoint=_temp(hold[REG_SYS_PV_SETPOINT]) or 0.0 if REG_SYS_PV_SETPOINT in hold else 0.0,
        )

    def _parse_heat_pump(self, inp: dict[int, int], hold: dict[int, int]) -> HeatPumpData:
        """Parse heat pump data from registers."""
        return HeatPumpData(
            operation_status=inp.get(REG_HP_OPERATION_STATUS, 0),
            error_status=inp.get(REG_HP_ERROR_STATUS, 0),
            power_request=inp.get(REG_HP_POWER_REQUEST, 0),
            flow_temp=_temp(inp[REG_HP_FLOW_TEMP]) if REG_HP_FLOW_TEMP in inp else None,
            return_temp=_temp(inp[REG_HP_RETURN_TEMP]) if REG_HP_RETURN_TEMP in inp else None,
            evaporator_temp=_temp(inp[REG_HP_EVAPORATOR_TEMP]) if REG_HP_EVAPORATOR_TEMP in inp else None,
            compressor_intake_temp=_temp(inp[REG_HP_COMPRESSOR_INTAKE_TEMP]) if REG_HP_COMPRESSOR_INTAKE_TEMP in inp else None,
            switch_temp=_temp(inp[REG_HP_SWITCH_TEMP]) if REG_HP_SWITCH_TEMP in inp else None,
            request_regen_temp=_temp(inp[REG_HP_REQUEST_REGEN]) if REG_HP_REQUEST_REGEN in inp else None,
            buffer_temp=_temp(inp[REG_HP_BUFFER_TEMP]) if REG_HP_BUFFER_TEMP in inp else None,
            precise_flow_temp=_temp(inp[REG_HP_PRECISE_FLOW_TEMP]) if REG_HP_PRECISE_FLOW_TEMP in inp else None,
            config=hold.get(REG_HP_CONFIG, 0),
            quiet_mode=hold.get(REG_HP_QUIET_MODE, 0),
            pump_start_mode=hold.get(REG_HP_PUMP_START_MODE, 0),
            pump_power_heating=hold.get(REG_HP_PUMP_POWER_HEATING, 0),
            pump_power_cooling=hold.get(REG_HP_PUMP_POWER_COOLING, 0),
            pump_power_hot_water=hold.get(REG_HP_PUMP_POWER_HOT_WATER, 0),
            pump_power_defrost=hold.get(REG_HP_PUMP_POWER_DEFROST, 0),
            flow_rate_heating=hold.get(REG_HP_FLOW_RATE_HEATING, 0),
            flow_rate_cooling=hold.get(REG_HP_FLOW_RATE_COOLING, 0),
            flow_rate_hot_water=hold.get(REG_HP_FLOW_RATE_HOT_WATER, 0),
        )

    def _parse_hot_water(self, inp: dict[int, int], hold: dict[int, int]) -> HotWaterData:
        """Parse hot water data from registers."""
        return HotWaterData(
            target_temp=_temp(inp[REG_WW_TARGET_TEMP]) if REG_WW_TARGET_TEMP in inp else None,
            current_temp=_temp(inp[REG_WW_CURRENT_TEMP]) if REG_WW_CURRENT_TEMP in inp else None,
            config=hold.get(REG_WW_CONFIG, 0),
            push_active=hold.get(REG_WW_PUSH, 0),
            normal_temp=_temp(hold[REG_WW_NORMAL_TEMP]) or 50.0 if REG_WW_NORMAL_TEMP in hold else 50.0,
            reduced_temp=_temp(hold[REG_WW_REDUCED_TEMP]) or 40.0 if REG_WW_REDUCED_TEMP in hold else 40.0,
            sg_ready_boost=_temp(hold[REG_WW_SG_READY_BOOST]) or 0.0 if REG_WW_SG_READY_BOOST in hold else 0.0,
        )

    def _parse_heating_circuit(self, inp: dict[int, int], hold: dict[int, int]) -> HeatingCircuitData:
        """Parse heating circuit data from registers."""
        return HeatingCircuitData(
            room_target_temp=_temp(inp[REG_HZ_ROOM_TARGET_TEMP]) if REG_HZ_ROOM_TARGET_TEMP in inp else None,
            room_temp=_temp(inp[REG_HZ_ROOM_TEMP]) if REG_HZ_ROOM_TEMP in inp else None,
            room_humidity=inp.get(REG_HZ_ROOM_HUMIDITY),
            flow_target_temp=_temp(inp[REG_HZ_FLOW_TARGET_TEMP]) if REG_HZ_FLOW_TARGET_TEMP in inp else None,
            flow_temp=_temp(inp[REG_HZ_FLOW_TEMP]) if REG_HZ_FLOW_TEMP in inp else None,
            config=hold.get(REG_HZ_CONFIG, 0),
            request_type=hold.get(REG_HZ_REQUEST_TYPE, 0),
            operation_mode=hold.get(REG_HZ_OPERATION_MODE, 0),
            party_pause=hold.get(REG_HZ_PARTY_PAUSE, 0),
            comfort_temp=_temp(hold[REG_HZ_COMFORT_TEMP]) or 22.0 if REG_HZ_COMFORT_TEMP in hold else 22.0,
            normal_temp=_temp(hold[REG_HZ_NORMAL_TEMP]) or 20.0 if REG_HZ_NORMAL_TEMP in hold else 20.0,
            reduced_temp=_temp(hold[REG_HZ_REDUCED_TEMP]) or 16.0 if REG_HZ_REDUCED_TEMP in hold else 16.0,
            heating_curve=hold.get(REG_HZ_HEATING_CURVE, 0) * TEMPERATURE_SCALE if REG_HZ_HEATING_CURVE in hold else 0.0,
            summer_winter_switch=_temp(hold[REG_HZ_SUMMER_WINTER_SWITCH]) or 0.0 if REG_HZ_SUMMER_WINTER_SWITCH in hold else 0.0,
            const_temp_heating=_temp(hold[REG_HZ_CONST_TEMP_HEATING]) or 0.0 if REG_HZ_CONST_TEMP_HEATING in hold else 0.0,
            const_temp_reduced=_temp(hold[REG_HZ_CONST_TEMP_REDUCED]) or 0.0 if REG_HZ_CONST_TEMP_REDUCED in hold else 0.0,
            const_temp_cooling=_temp(hold[REG_HZ_CONST_TEMP_COOLING]) or 0.0 if REG_HZ_CONST_TEMP_COOLING in hold else 0.0,
        )

    def _parse_secondary_heater(self, inp: dict[int, int], hold: dict[int, int]) -> SecondaryHeaterData:
        """Parse secondary heater data from registers."""
        return SecondaryHeaterData(
            status=inp.get(REG_W2_STATUS, 0),
            eheater1_cycles=inp.get(REG_W2_EHEATER1_CYCLES, 0),
            eheater1_hours=inp.get(REG_W2_EHEATER1_HOURS, 0),
            eheater1_status=inp.get(REG_W2_EHEATER1_STATUS, 0),
            eheater2_status=inp.get(REG_W2_EHEATER2_STATUS, 0),
            eheater2_cycles=inp.get(REG_W2_EHEATER2_CYCLES, 0),
            eheater2_hours=inp.get(REG_W2_EHEATER2_HOURS, 0),
            config=hold.get(REG_W2_CONFIG, 0),
            ep1_config=hold.get(REG_W2_EP1_CONFIG, 0),
            ep2_config=hold.get(REG_W2_EP2_CONFIG, 0),
            limit_temp=_temp(hold[REG_W2_LIMIT_TEMP]) or 0.0 if REG_W2_LIMIT_TEMP in hold else 0.0,
            bivalence_temp=_temp(hold[REG_W2_BIVALENCE_TEMP]) or 0.0 if REG_W2_BIVALENCE_TEMP in hold else 0.0,
            bivalence_temp_ww=_temp(hold[REG_W2_BIVALENCE_TEMP_WW]) or 0.0 if REG_W2_BIVALENCE_TEMP_WW in hold else 0.0,
        )

    def _parse_statistics(self, inp: dict[int, int]) -> StatisticsData:
        """Parse statistics from registers."""
        def _block(today_addr: int) -> EnergyBlock:
            return EnergyBlock(
                today=_energy(inp.get(today_addr, 0)),
                yesterday=_energy(inp.get(today_addr + 1, 0)),
                month=_energy(inp.get(today_addr + 2, 0)),
                year=_energy(inp.get(today_addr + 3, 0)),
            )

        return StatisticsData(
            total=_block(REG_ST_TOTAL_ENERGY_TODAY),
            heating=_block(REG_ST_HEATING_ENERGY_TODAY),
            hot_water=_block(REG_ST_HOT_WATER_ENERGY_TODAY),
            cooling=_block(REG_ST_COOLING_ENERGY_TODAY),
            defrost=_block(REG_ST_DEFROST_ENERGY_TODAY),
            total2=_block(REG_ST_TOTAL2_ENERGY_TODAY),
            electric=_block(REG_ST_ELEC_ENERGY_TODAY),
        )

    async def async_identify_device(self) -> DeviceInfo:
        """Read device identification from the heat pump."""
        await self.connect()
        return DeviceInfo(
            device_type="Weishaupt WBB",
            firmware_version="unknown",
            serial_number=f"wcm_{self._host}",
        )

    async def async_read_all(self) -> WeishauptData:
        """Read all registers and return a complete data snapshot."""
        async with self._lock:
            inp = await self._read_all_input_registers()
            hold = await self._read_all_holding_registers()

        return WeishauptData(
            system=self._parse_system(inp, hold),
            heat_pump=self._parse_heat_pump(inp, hold),
            hot_water=self._parse_hot_water(inp, hold),
            heating_circuit=self._parse_heating_circuit(inp, hold),
            secondary_heater=self._parse_secondary_heater(inp, hold),
            statistics=self._parse_statistics(inp),
            device_info=await self.async_identify_device(),
        )
