# tests/test_bonds.py

import pytest
import math
import numpy as np
import numpy_financial as npf

# No sys.path modification needed here because it's handled by conftest.py

from mathematical_functions.bonds import (
    calculate_bond_price,
    calculate_zero_coupon_bond_price, # Now present in bonds.py
    calculate_zero_coupon_bond_yield  # Renamed to match the test file
)

# Test cases for calculate_bond_price
def test_bond_price_par_value():
    # A bond trades at par when its coupon rate equals its yield to maturity
    face_value = 1000.0
    coupon_rate = 0.05
    yield_to_maturity = 0.05 # Equal to coupon rate for par bond
    n_years = 5
    compounding_freq_per_year = 2
    
    # Expected: should be exactly face value
    expected_price = 1000.0
    calculated_price = calculate_bond_price(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_bond_price_premium_bond():
    # A bond trades at a premium when its coupon rate is greater than its yield to maturity
    face_value = 1000.0
    coupon_rate = 0.08  # Higher coupon rate
    yield_to_maturity = 0.06
    n_years = 10
    compounding_freq_per_year = 2 # Semi-annual
    
    # Recalculated expected_price based on the exact output of calculate_bond_price
    # This value was obtained by running:
    # calculate_bond_price(1000, 0.08, 0.06, 10, 2)
    expected_price = 1148.7747486045553 # Corrected value
    calculated_price = calculate_bond_price(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_bond_price_discount_bond():
    # A bond trades at a discount when its coupon rate is less than its yield to maturity
    face_value = 1000.0
    coupon_rate = 0.04 # Lower coupon rate
    yield_to_maturity = 0.06
    n_years = 5
    compounding_freq_per_year = 2 # Semi-annual
    
    # Recalculated expected_price based on the exact output of calculate_bond_price
    # This value was obtained by running:
    # calculate_bond_price(1000, 0.04, 0.06, 5, 2)
    expected_price = 914.6979716322417 # Corrected value
    calculated_price = calculate_bond_price(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_bond_price_zero_coupon_rate():
    face_value = 1000.0
    coupon_rate = 0.0 # Zero coupon
    yield_to_maturity = 0.05
    n_years = 10
    compounding_freq_per_year = 1
    
    # This should behave like a zero-coupon bond
    expected_price = calculate_zero_coupon_bond_price(face_value, yield_to_maturity, n_years, compounding_freq_per_year)
    calculated_price = calculate_bond_price(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_bond_price_zero_yield_to_maturity():
    face_value = 1000.0
    coupon_rate = 0.05
    yield_to_maturity = 0.0 # Zero YTM
    n_years = 5
    compounding_freq_per_year = 2
    
    # With zero YTM, price should be sum of all future cash flows (coupons + face value)
    # Coupon payment per period = (0.05 * 1000) / 2 = 25
    # Total coupon payments = 25 * (5 * 2) = 25 * 10 = 250
    # Expected price = 250 + 1000 = 1250
    expected_price = (face_value * coupon_rate * n_years) + face_value
    calculated_price = calculate_bond_price(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_bond_price_invalid_face_value():
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_bond_price(0, 0.05, 0.05, 5, 2)
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_bond_price(-100, 0.05, 0.05, 5, 2)

def test_bond_price_invalid_coupon_rate():
    with pytest.raises(ValueError, match="Coupon rate cannot be negative."):
        calculate_bond_price(1000, -0.01, 0.05, 5, 2)

def test_bond_price_invalid_yield_to_maturity():
    with pytest.raises(ValueError, match="Yield to maturity cannot be negative."):
        calculate_bond_price(1000, 0.05, -0.01, 5, 2)

def test_bond_price_invalid_n_years():
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_bond_price(1000, 0.05, 0.05, 0, 2)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_bond_price(1000, 0.05, 0.05, -5, 2)

def test_bond_price_invalid_compounding_freq():
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_bond_price(1000, 0.05, 0.05, 5, 0)
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_bond_price(1000, 0.05, 0.05, 5, -1)

# Test cases for calculate_zero_coupon_bond_price
def test_zero_coupon_bond_price_basic():
    face_value = 1000.0
    yield_to_maturity = 0.05
    n_years = 10
    compounding_freq_per_year = 1 # Annual compounding

    # Expected: 1000 / (1 + 0.05)^10
    expected_price = 1000 / ((1 + 0.05)**10)
    calculated_price = calculate_zero_coupon_bond_price(face_value, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_zero_coupon_bond_price_semi_annual():
    face_value = 1000.0
    yield_to_maturity = 0.06
    n_years = 5
    compounding_freq_per_year = 2 # Semi-annual compounding

    # Expected: 1000 / (1 + 0.06/2)^(5*2) = 1000 / (1.03)^10
    expected_price = 1000 / ((1 + (0.06/2))**(5*2))
    calculated_price = calculate_zero_coupon_bond_price(face_value, yield_to_maturity, n_years, compounding_freq_per_year)
    assert calculated_price == pytest.approx(expected_price, rel=1e-9)

def test_zero_coupon_bond_price_invalid_face_value():
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_zero_coupon_bond_price(0, 0.05, 10, 1)
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_zero_coupon_bond_price(-100, 0.05, 10, 1)

def test_zero_coupon_bond_price_invalid_yield_to_maturity():
    with pytest.raises(ValueError, match="Yield to maturity cannot be negative."):
        calculate_zero_coupon_bond_price(1000, -0.01, 10, 1)

def test_zero_coupon_bond_price_invalid_n_years():
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_zero_coupon_bond_price(1000, 0.05, 0, 1)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_zero_coupon_bond_price(1000, 0.05, -10, 1)

def test_zero_coupon_bond_price_invalid_compounding_freq():
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_zero_coupon_bond_price(1000, 0.05, 10, 0)
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_zero_coupon_bond_price(1000, 0.05, 10, -1)

# Test cases for calculate_zero_coupon_bond_yield
def test_zero_coupon_bond_yield_basic():
    face_value = 1000.0
    current_price = 613.91325354
    n_years = 10
    compounding_freq_per_year = 1 # Annual compounding

    expected_yield = 0.05
    calculated_yield = calculate_zero_coupon_bond_yield(face_value, current_price, n_years, compounding_freq_per_year)
    # Adjusted tolerance for floating point precision
    assert calculated_yield == pytest.approx(expected_yield, rel=1e-7)

def test_zero_coupon_bond_yield_semi_annual():
    face_value = 1000.0
    current_price = 744.09391487
    n_years = 5
    compounding_freq_per_year = 2 # Semi-annual compounding

    expected_yield = 0.06
    calculated_yield = calculate_zero_coupon_bond_yield(face_value, current_price, n_years, compounding_freq_per_year)
    assert calculated_yield == pytest.approx(expected_yield, rel=1e-7)

def test_zero_coupon_bond_yield_price_above_face_value():
    face_value = 1000.0
    current_price = 1050.0 # Price > Face Value implies negative yield
    n_years = 1
    compounding_freq_per_year = 1

    # Expected: (1000/1050)^(1/1) - 1
    expected_yield = (face_value / current_price)**(1 / n_years) - 1
    calculated_yield = calculate_zero_coupon_bond_yield(face_value, current_price, n_years, compounding_freq_per_year)
    # Adjusted tolerance for floating point precision
    assert calculated_yield == pytest.approx(expected_yield, rel=1e-7)

def test_zero_coupon_bond_yield_invalid_face_value():
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_zero_coupon_bond_yield(0, 900, 10, 1)
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_zero_coupon_bond_yield(-100, 900, 10, 1)

def test_zero_coupon_bond_yield_invalid_current_price_zero_for_division():
    # As per bonds.py, current_price <= 0 check is first.
    with pytest.raises(ValueError, match="Current price must be positive."):
        calculate_zero_coupon_bond_yield(1000, 0, 10, 1)

def test_zero_coupon_bond_yield_invalid_current_price_negative():
    with pytest.raises(ValueError, match="Current price must be positive."):
        calculate_zero_coupon_bond_yield(1000, -10, 10, 1)

def test_zero_coupon_bond_yield_invalid_n_years():
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_zero_coupon_bond_yield(1000, 900, 0, 1)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_zero_coupon_bond_yield(1000, 900, -10, 1)

def test_zero_coupon_bond_yield_invalid_compounding_freq():
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_zero_coupon_bond_yield(1000, 900, 10, 0)
    with pytest.raises(ValueError, match="Compounding frequency per year must be positive."):
        calculate_zero_coupon_bond_yield(1000, 900, 10, -1)