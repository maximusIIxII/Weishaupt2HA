"""Exceptions for Weishaupt Modbus communication."""


class WeishauptModbusError(Exception):
    """Base exception for Weishaupt Modbus errors."""


class WeishauptConnectionError(WeishauptModbusError):
    """Connection to the WCM-COM module failed."""


class WeishauptReadError(WeishauptModbusError):
    """Reading registers from the heat pump failed."""


class WeishauptWriteError(WeishauptModbusError):
    """Writing a register to the heat pump failed."""
