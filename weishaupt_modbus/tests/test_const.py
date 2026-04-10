"""Tests for Weishaupt Modbus constants."""

from weishaupt_modbus.const import (
    HOLDING_REGISTER_BLOCKS,
    INPUT_REGISTER_BLOCKS,
    HeatingCircuitMode,
    HeatPumpOperationStatus,
    SystemOperationMode,
)


def test_system_operation_modes():
    """Test that system operation mode enum values are correct."""
    assert SystemOperationMode.AUTO == 0
    assert SystemOperationMode.HEATING == 1
    assert SystemOperationMode.STANDBY == 4


def test_heat_pump_operation_status():
    """Test heat pump operation status enum."""
    assert HeatPumpOperationStatus.STANDBY == 0
    assert HeatPumpOperationStatus.HEATING == 1
    assert HeatPumpOperationStatus.HOT_WATER == 2
    assert HeatPumpOperationStatus.DEFROST == 3


def test_heating_circuit_modes():
    """Test heating circuit mode enum."""
    assert HeatingCircuitMode.AUTO == 0
    assert HeatingCircuitMode.COMFORT == 1
    assert HeatingCircuitMode.STANDBY == 4


def test_register_blocks_no_overlap():
    """Test that register blocks don't overlap."""
    all_addresses: set[int] = set()
    for start, count in INPUT_REGISTER_BLOCKS + HOLDING_REGISTER_BLOCKS:
        for addr in range(start, start + count):
            assert addr not in all_addresses, f"Duplicate address {addr}"
            all_addresses.add(addr)


def test_register_blocks_not_empty():
    """Test that register block lists are populated."""
    assert len(INPUT_REGISTER_BLOCKS) > 0
    assert len(HOLDING_REGISTER_BLOCKS) > 0
