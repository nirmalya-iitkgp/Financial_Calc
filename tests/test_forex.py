# tests/test_forex.py

import pytest
from mathematical_functions.forex import (
    convert_currency,
    calculate_forward_rate # This is the function actually defined in forex.py
)
import math

# --- convert_currency tests ---
def test_convert_currency_basic():
    """Test basic currency conversion."""
    # 100 USD to EUR, rate 0.92 EUR/USD -> 92 EUR
    assert convert_currency(100, 0.92) == pytest.approx(92.0)
    # 500 JPY to USD, rate 0.0075 USD/JPY -> 3.75 USD
    assert convert_currency(500, 0.0075) == pytest.approx(3.75)

def test_convert_currency_one_to_one_rate():
    """Test conversion with a 1:1 exchange rate."""
    assert convert_currency(100, 1.0) == pytest.approx(100.0)

def test_convert_currency_zero_amount():
    """Test conversion with zero amount."""
    assert convert_currency(0, 0.92) == pytest.approx(0.0)

def test_convert_currency_invalid_negative_amount():
    """Test conversion with a negative amount."""
    with pytest.raises(ValueError, match="Amount to convert cannot be negative."):
        convert_currency(-100, 0.92)

def test_convert_currency_invalid_non_positive_spot_rate():
    """Test conversion with non-positive spot rate."""
    with pytest.raises(ValueError, match="Spot rate must be positive."):
        convert_currency(100, 0)
    with pytest.raises(ValueError, match="Spot rate must be positive."):
        convert_currency(100, -0.5)

# --- calculate_forward_rate_interest_rate_parity tests ---
# IMPORTANT: Renamed calls from 'calculate_forward_rate_interest_rate_parity' to 'calculate_forward_rate'
def test_forward_rate_interest_rate_parity_basic():
    """Test forward rate calculation with basic parameters."""
    # S = 1.20 (EUR/USD), r_dom = 0.05 (EUR), r_for = 0.03 (USD), T = 1 year
    # F = 1.20 * ( (1+0.05)^1 / (1+0.03)^1 ) = 1.20 * (1.05 / 1.03) = 1.2233
    assert calculate_forward_rate(1.20, 0.05, 0.03, 1) == pytest.approx(1.22330, rel=1e-4)

def test_forward_rate_interest_rate_parity_short_term():
    """Test forward rate for a shorter time to maturity."""
    # S = 1.30 (GBP/USD), r_dom = 0.04 (GBP), r_for = 0.02 (USD), T = 0.5 years
    # F = 1.30 * ( (1+0.04)^0.5 / (1+0.02)^0.5 )
    assert calculate_forward_rate(1.30, 0.04, 0.02, 0.5) == pytest.approx(1.31278, rel=1e-4)

def test_forward_rate_interest_rate_parity_equal_rates():
    """Test forward rate when domestic and foreign rates are equal (forward rate = spot rate)."""
    assert calculate_forward_rate(1.10, 0.05, 0.05, 2) == pytest.approx(1.10)

def test_forward_rate_interest_rate_parity_zero_rates():
    """Test forward rate when both interest rates are zero (forward rate = spot rate)."""
    assert calculate_forward_rate(1.10, 0, 0, 2) == pytest.approx(1.10)

def test_forward_rate_interest_rate_parity_invalid_spot_rate():
    """Test forward rate with non-positive spot rate."""
    with pytest.raises(ValueError, match="Spot rate must be positive."):
        calculate_forward_rate(0, 0.05, 0.03, 1)
    with pytest.raises(ValueError, match="Spot rate must be positive."):
        calculate_forward_rate(-1.0, 0.05, 0.03, 1)

def test_forward_rate_interest_rate_parity_invalid_time_to_maturity():
    """Test forward rate with non-positive time to maturity."""
    with pytest.raises(ValueError, match="Time to maturity must be positive."):
        calculate_forward_rate(1.20, 0.05, 0.03, 0)
    with pytest.raises(ValueError, match="Time to maturity must be positive."):
        calculate_forward_rate(1.20, 0.05, 0.03, -1)

def test_forward_rate_interest_rate_parity_invalid_domestic_rate():
    """Test forward rate with invalid domestic rate (less than -1)."""
    with pytest.raises(ValueError, match="Interest rates must be greater than -1"):
        calculate_forward_rate(1.20, -1.1, 0.03, 1)

def test_forward_rate_interest_rate_parity_invalid_foreign_rate():
    """Test forward rate with invalid foreign rate (less than -1)."""
    with pytest.raises(ValueError, match="Interest rates must be greater than -1"):
        calculate_forward_rate(1.20, 0.05, -1.1, 1)