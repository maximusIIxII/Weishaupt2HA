"""Tests for Weishaupt Modbus data models."""

from weishaupt_modbus.models import (
    EnergyBlock,
    HeatingCircuitData,
    HeatPumpData,
    HotWaterData,
    StatisticsData,
    SystemData,
    WeishauptData,
)


def test_weishaupt_data_defaults():
    """Test that WeishauptData initializes with sensible defaults."""
    data = WeishauptData()
    assert data.system.outdoor_temp is None
    assert data.system.error_code == 65535  # no error
    assert data.heat_pump.flow_temp is None
    assert data.hot_water.normal_temp == 50.0
    assert data.heating_circuit.comfort_temp == 22.0
    assert data.statistics.total.today == 0.0


def test_system_data():
    """Test SystemData fields."""
    sys = SystemData(outdoor_temp=5.3, error_code=65535, operation_mode=1)
    assert sys.outdoor_temp == 5.3
    assert sys.error_code == 65535
    assert sys.operation_mode == 1


def test_heat_pump_data():
    """Test HeatPumpData fields."""
    hp = HeatPumpData(flow_temp=35.2, return_temp=28.1, power_request=75.0)
    assert hp.flow_temp == 35.2
    assert hp.return_temp == 28.1
    assert hp.power_request == 75.0


def test_hot_water_data():
    """Test HotWaterData fields."""
    ww = HotWaterData(current_temp=48.5, target_temp=50.0, push_active=1)
    assert ww.current_temp == 48.5
    assert ww.push_active == 1


def test_heating_circuit_data():
    """Test HeatingCircuitData fields."""
    hz = HeatingCircuitData(
        room_temp=21.5,
        comfort_temp=22.0,
        heating_curve=0.8,
        operation_mode=0,
    )
    assert hz.room_temp == 21.5
    assert hz.heating_curve == 0.8


def test_energy_block():
    """Test EnergyBlock fields."""
    eb = EnergyBlock(today=12.5, yesterday=15.3, month=350.0, year=4200.0)
    assert eb.today == 12.5
    assert eb.year == 4200.0


def test_statistics_data():
    """Test StatisticsData with nested EnergyBlocks."""
    stats = StatisticsData(
        total=EnergyBlock(today=20.0),
        electric=EnergyBlock(today=5.0),
    )
    assert stats.total.today == 20.0
    assert stats.electric.today == 5.0
    # COP can be calculated: total/electric
    assert stats.total.today / stats.electric.today == 4.0
