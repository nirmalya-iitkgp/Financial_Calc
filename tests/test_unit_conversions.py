# tests/test_unit_conversions.py

import pytest
from mathematical_functions.unit_conversions import convert_time_periods

# --- convert_time_periods tests ---
def test_convert_time_periods_days_to_years():
    """Test conversion from days to years."""
    assert convert_time_periods(365, 'days', 'years') == pytest.approx(1.0)
    assert convert_time_periods(730, 'days', 'years') == pytest.approx(2.0)
    assert convert_time_periods(182.5, 'days', 'years') == pytest.approx(0.5)

def test_convert_time_periods_months_to_quarters():
    """Test conversion from months to quarters."""
    assert convert_time_periods(3, 'months', 'quarters') == pytest.approx(1.0)
    assert convert_time_periods(6, 'months', 'quarters') == pytest.approx(2.0)
    assert convert_time_periods(18, 'months', 'quarters') == pytest.approx(6.0)

def test_convert_time_periods_years_to_months():
    """Test conversion from years to months."""
    assert convert_time_periods(1, 'years', 'months') == pytest.approx(12.0)
    assert convert_time_periods(2.5, 'years', 'months') == pytest.approx(30.0)

def test_convert_time_periods_weeks_to_days():
    """Test conversion from weeks to days."""
    assert convert_time_periods(1, 'weeks', 'days') == pytest.approx(7.0)
    assert convert_time_periods(0.5, 'weeks', 'days') == pytest.approx(3.5)

def test_convert_time_periods_case_insensitivity():
    """Test unit names are case-insensitive."""
    assert convert_time_periods(1, 'Years', 'MONTHS') == pytest.approx(12.0)
    assert convert_time_periods(365, 'DAYS', 'years') == pytest.approx(1.0)

def test_convert_time_periods_same_unit():
    """Test conversion to the same unit."""
    assert convert_time_periods(100, 'days', 'days') == pytest.approx(100.0)
    assert convert_time_periods(5, 'years', 'years') == pytest.approx(5.0)

def test_convert_time_periods_zero_value():
    """Test conversion with a zero input value."""
    assert convert_time_periods(0, 'days', 'years') == pytest.approx(0.0)
    assert convert_time_periods(0, 'years', 'months') == pytest.approx(0.0)

def test_convert_time_periods_invalid_negative_value():
    """Test conversion with a negative input value."""
    with pytest.raises(ValueError, match="Time value to convert cannot be negative."):
        convert_time_periods(-10, 'days', 'years')

def test_convert_time_periods_unsupported_from_unit():
    """Test conversion with an unsupported 'from' unit."""
    with pytest.raises(ValueError, match="Unsupported 'from_unit':.*Supported units are:"):
        convert_time_periods(10, 'seconds', 'years')

def test_convert_time_periods_unsupported_to_unit():
    """Test conversion with an unsupported 'to' unit."""
    with pytest.raises(ValueError, match="Unsupported 'to_unit':.*Supported units are:"):
        convert_time_periods(10, 'years', 'fortnights')