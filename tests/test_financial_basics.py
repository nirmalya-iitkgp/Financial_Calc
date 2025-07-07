# tests/test_financial_basics.py

import pytest
from mathematical_functions.financial_basics import (
    calculate_perpetuity,
    calculate_growing_perpetuity
)

# --- calculate_perpetuity tests ---
def test_perpetuity_basic():
    """Test perpetuity calculation with basic positive values."""
    # $100 payment per period, 5% rate -> 100 / 0.05 = 2000
    assert calculate_perpetuity(100, 0.05) == pytest.approx(2000.0)

def test_perpetuity_different_values():
    """Test perpetuity with different payment and rate."""
    assert calculate_perpetuity(50, 0.02) == pytest.approx(2500.0)
    assert calculate_perpetuity(1000, 0.10) == pytest.approx(10000.0)

def test_perpetuity_zero_payment():
    """Test perpetuity with zero payment (should be zero)."""
    assert calculate_perpetuity(0, 0.05) == pytest.approx(0.0)

def test_perpetuity_negative_payment():
    """Test perpetuity with a negative payment (outflow)."""
    assert calculate_perpetuity(-100, 0.05) == pytest.approx(-2000.0)

def test_perpetuity_invalid_zero_rate():
    """Test perpetuity with zero discount rate (division by zero)."""
    with pytest.raises(ValueError, match="The discount rate \(rate\) for a perpetuity must be greater than 0."):
        calculate_perpetuity(100, 0)

def test_perpetuity_invalid_negative_rate():
    """Test perpetuity with negative discount rate (can lead to non-sensical values)."""
    with pytest.raises(ValueError, match="The discount rate \(rate\) for a perpetuity must be greater than 0."):
        calculate_perpetuity(100, -0.05)

# --- calculate_growing_perpetuity tests ---
def test_growing_perpetuity_basic():
    """Test growing perpetuity calculation with basic values."""
    # D1=100, r=0.10, g=0.05 -> 100 / (0.10 - 0.05) = 100 / 0.05 = 2000
    assert calculate_growing_perpetuity(100, 0.10, 0.05) == pytest.approx(2000.0)

def test_growing_perpetuity_different_values():
    """Test growing perpetuity with different parameters."""
    # D1=50, r=0.08, g=0.03 -> 50 / (0.08 - 0.03) = 50 / 0.05 = 1000
    assert calculate_growing_perpetuity(50, 0.08, 0.03) == pytest.approx(1000.0)
    # D1=10, r=0.06, g=0.01 -> 10 / (0.06 - 0.01) = 10 / 0.05 = 200
    assert calculate_growing_perpetuity(10, 0.06, 0.01) == pytest.approx(200.0)

def test_growing_perpetuity_zero_payment_year1():
    """Test growing perpetuity with zero first payment."""
    assert calculate_growing_perpetuity(0, 0.10, 0.05) == pytest.approx(0.0)

def test_growing_perpetuity_negative_payment_year1():
    """Test growing perpetuity with negative first payment."""
    assert calculate_growing_perpetuity(-100, 0.10, 0.05) == pytest.approx(-2000.0)

def test_growing_perpetuity_invalid_rate_le_growth_rate():
    """Test growing perpetuity where rate is less than or equal to growth rate."""
    # r = g
    with pytest.raises(ValueError, match="The discount rate \(rate\) must be strictly greater than the growth rate \(growth_rate\).*"):
        calculate_growing_perpetuity(100, 0.05, 0.05)
    # r < g
    with pytest.raises(ValueError, match="The discount rate \(rate\) must be strictly greater than the growth rate \(growth_rate\).*"):
        calculate_growing_perpetuity(100, 0.05, 0.10)
    # r < 0, g < 0 but r <= g
    with pytest.raises(ValueError, match="The discount rate \(rate\) must be strictly greater than the growth rate \(growth_rate\).*"):
        calculate_growing_perpetuity(100, -0.05, -0.01)