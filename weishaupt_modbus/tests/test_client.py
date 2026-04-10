"""Tests for Weishaupt Modbus client — helper functions."""

from weishaupt_modbus.client import _signed, _temp, _energy


def test_signed_positive():
    """Test signed conversion for positive values."""
    assert _signed(215) == 215
    assert _signed(0) == 0
    assert _signed(32767) == 32767


def test_signed_negative():
    """Test signed conversion for negative values."""
    assert _signed(65535) == -1
    assert _signed(65536 - 50) == -50
    assert _signed(32768) == -32768


def test_temp_normal():
    """Test temperature conversion for normal values."""
    assert _temp(215) == 21.5
    assert _temp(350) == 35.0
    assert _temp(0) == 0.0


def test_temp_negative():
    """Test temperature conversion for negative values."""
    assert _temp(65536 - 50) == -5.0
    assert _temp(65536 - 100) == -10.0


def test_temp_invalid():
    """Test temperature conversion for invalid sentinel values."""
    # 32768 unsigned = -32768 signed → invalid
    assert _temp(32768) is None
    assert _temp(32767) is None


def test_energy():
    """Test energy conversion."""
    assert _energy(125) == 12.5
    assert _energy(0) == 0.0
    assert _energy(42000) == 4200.0
