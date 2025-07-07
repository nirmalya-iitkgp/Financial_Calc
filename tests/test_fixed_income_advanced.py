# tests/test_fixed_income_advanced.py

import pytest
from mathematical_functions.fixed_income_advanced import (
    calculate_macaulay_duration,
    calculate_convexity,
    calculate_forward_rate,
    calculate_yield_curve_spot_rate,
    calculate_par_rate,
    bootstrap_yield_curve
)
import numpy as np
import math

# Common bond parameters for testing
FACE_VALUE = 1000.0
COUPON_RATE = 0.05 # 5% annual
YTM = 0.06         # 6% annual
N_YEARS = 3.0      # 3 years to maturity
COMP_FREQ = 2      # Semi-annual compounding

# --- calculate_macaulay_duration tests ---
def test_macaulay_duration_basic():
    """Test Macaulay Duration calculation with a basic bond."""
    # Recalculated for 1000 FV, 5% coupon, 6% YTM, 3 years, semi-annual
    # Expected Macaulay Duration: ~2.8200 years
    assert calculate_macaulay_duration(FACE_VALUE, COUPON_RATE, YTM, N_YEARS, COMP_FREQ) == pytest.approx(2.8200, rel=1e-4)

def test_macaulay_duration_zero_coupon():
    """Test Macaulay Duration for a zero-coupon bond (should equal maturity)."""
    assert calculate_macaulay_duration(1000, 0, 0.05, 5, 1) == pytest.approx(5.0)
    assert calculate_macaulay_duration(1000, 0, 0.05, 2, 4) == pytest.approx(2.0)

def test_macaulay_duration_at_par():
    """Test Macaulay Duration when coupon rate equals YTM."""
    # Recalculated for 1000 FV, 5% coupon, 5% YTM, 5 years, semi-annual
    # Expected Macaulay Duration: ~4.4854 years
    assert calculate_macaulay_duration(1000, 0.05, 0.05, 5, 2) == pytest.approx(4.4854, rel=1e-4)

def test_macaulay_duration_invalid_inputs():
    """Test Macaulay Duration with invalid inputs."""
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_macaulay_duration(0, COUPON_RATE, YTM, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match="Coupon rate cannot be negative."):
        calculate_macaulay_duration(FACE_VALUE, -0.01, YTM, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match=r"Yield to maturity cannot be less than -1 \(or -100%\)\."):
        calculate_macaulay_duration(FACE_VALUE, COUPON_RATE, -1.1, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_macaulay_duration(FACE_VALUE, COUPON_RATE, YTM, 0, COMP_FREQ)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        calculate_macaulay_duration(FACE_VALUE, COUPON_RATE, YTM, N_YEARS, 0)
    
    # Test for bond price effectively zero due to very high YTM
    with pytest.raises(ValueError, match=r"Bond price \(sum of PV of cash flows\) is effectively zero, Macaulay duration is undefined."):
        calculate_macaulay_duration(FACE_VALUE, COUPON_RATE, 100.0, N_YEARS, COMP_FREQ) # YTM = 100%

# --- calculate_convexity tests ---
def test_convexity_basic():
    """Test Convexity calculation with a basic bond."""
    # Recalculated for 1000 FV, 5% coupon, 6% YTM, 3 years, semi-annual
    # Expected Convexity: ~9.1093 years^2
    assert calculate_convexity(FACE_VALUE, COUPON_RATE, YTM, N_YEARS, COMP_FREQ) == pytest.approx(9.1093, rel=1e-2)

def test_convexity_zero_coupon():
    """Test Convexity for a zero-coupon bond."""
    # For T=5 years, YTM=0.05, Compounding=Annually (1)
    # Expected Convexity: (N_periods * (N_periods + 1)) / ((1+periodic_yield)^2 * (comp_freq)^2 )
    # (5 * (5+1)) / ((1+0.05)^2 * 1^2) = 30 / 1.1025 = 27.21088
    assert calculate_convexity(1000, 0, 0.05, 5, 1) == pytest.approx(27.2109, rel=1e-4)

def test_convexity_invalid_inputs():
    """Test Convexity with invalid inputs."""
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_convexity(0, COUPON_RATE, YTM, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match="Coupon rate cannot be negative."):
        calculate_convexity(FACE_VALUE, -0.01, YTM, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match=r"Yield to maturity cannot be less than -1 \(or -100%\)\."):
        calculate_convexity(FACE_VALUE, COUPON_RATE, -1.1, N_YEARS, COMP_FREQ)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_convexity(FACE_VALUE, COUPON_RATE, YTM, 0, COMP_FREQ)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        calculate_convexity(FACE_VALUE, COUPON_RATE, YTM, N_YEARS, 0)
    
    # Test for zero YTM (specific handling in function)
    with pytest.raises(ValueError, match="Convexity calculation is not precisely defined for zero yield to maturity in this implementation."):
        calculate_convexity(FACE_VALUE, COUPON_RATE, 0.0, N_YEARS, COMP_FREQ)
    
    # Test for bond price effectively zero due to very high YTM
    with pytest.raises(ValueError, match="Bond price is effectively zero, convexity is undefined."):
        calculate_convexity(FACE_VALUE, COUPON_RATE, 100.0, N_YEARS, COMP_FREQ) # YTM = 100%

# --- calculate_forward_rate tests ---
def test_forward_rate_basic():
    """Test implied forward rate calculation with basic spot rates."""
    # 1-year spot = 4%, 2-year spot = 5%
    # F(1,2) = [((1.05)^2) / ((1.04)^1)]^(1/(2-1)) - 1 = 0.0600961538...
    assert calculate_forward_rate(0.04, 1, 0.05, 2) == pytest.approx(0.060096, rel=1e-4)

def test_forward_rate_flat_yield_curve():
    """Test forward rate when spot rates are equal (should be equal to spot rate)."""
    assert calculate_forward_rate(0.05, 1, 0.05, 2) == pytest.approx(0.05)
    assert calculate_forward_rate(0.03, 2, 0.03, 5) == pytest.approx(0.03)

def test_forward_rate_inverted_yield_curve():
    """Test forward rate with an inverted yield curve."""
    # 1-year spot = 6%, 2-year spot = 5%
    # F(1,2) = [((1.05)^2) / ((1.06)^1)]^(1/(2-1)) - 1 = 0.0400943396...
    assert calculate_forward_rate(0.06, 1, 0.05, 2) == pytest.approx(0.040094, rel=1e-4)

def test_forward_rate_invalid_t1_ge_t2():
    """Test forward rate with invalid time periods (t1 >= t2)."""
    with pytest.raises(ValueError, match="t1_years must be strictly less than t2_years to calculate a forward rate."):
        calculate_forward_rate(0.04, 1, 0.05, 1) # t1=t2
    with pytest.raises(ValueError, match="t1_years must be strictly less than t2_years to calculate a forward rate."):
        calculate_forward_rate(0.04, 2, 0.05, 1) # t1 > t2

def test_forward_rate_invalid_non_positive_years():
    """Test forward rate with non-positive years."""
    with pytest.raises(ValueError, match=r"Maturity years \(t1_years, t2_years\) must be positive\."):
        calculate_forward_rate(0.04, 0, 0.05, 2)
    with pytest.raises(ValueError, match=r"Maturity years \(t1_years, t2_years\) must be positive\."):
        calculate_forward_rate(0.04, 1, 0.05, 0)

def test_forward_rate_invalid_rates_below_neg_one():
    """Test forward rate with invalid rates (less than -1)."""
    with pytest.raises(ValueError, match=r"Spot rates cannot be less than -1 \(or -100%\)\."):
        calculate_forward_rate(-1.1, 1, 0.05, 2)
    with pytest.raises(ValueError, match=r"Spot rates cannot be less than -1 \(or -100%\)\."):
        calculate_forward_rate(0.04, 1, -1.1, 2)

# --- calculate_yield_curve_spot_rate tests ---
def test_calculate_yield_curve_spot_rate_basic():
    """Test basic spot rate calculation from ZCB price."""
    # Price = 950, FV = 1000, N = 1 year => (1000/950)^(1/1) - 1 = 0.052631...
    assert calculate_yield_curve_spot_rate(950, 1000, 1) == pytest.approx(0.052631, rel=1e-4)
    # Price = 800, FV = 1000, N = 5 years => (1000/800)^(1/5) - 1 = 0.045638...
    assert calculate_yield_curve_spot_rate(800, 1000, 5) == pytest.approx(0.045638, rel=1e-4)

def test_calculate_yield_curve_spot_rate_invalid_inputs():
    """Test spot rate calculation with invalid inputs."""
    with pytest.raises(ValueError, match="Zero-coupon bond price must be positive."):
        calculate_yield_curve_spot_rate(0, 1000, 1)
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_yield_curve_spot_rate(950, 0, 1)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_yield_curve_spot_rate(950, 1000, 0)

# --- calculate_par_rate tests ---
def test_calculate_par_rate_basic():
    """Test basic par rate calculation with given spot rates."""
    # Example: 1-yr spot 5%, 2-yr spot 6%, 3-yr spot 7%
    # Recalculated precisely: 0.06909535934355727
    spot_rates = [0.05, 0.06, 0.07]
    maturities = [1, 2, 3]
    assert calculate_par_rate(spot_rates, maturities) == pytest.approx(0.06909536, rel=1e-6) # Increased precision for approx

def test_calculate_par_rate_flat_curve():
    """Test par rate with a flat yield curve (should equal spot rate)."""
    spot_rates = [0.05, 0.05, 0.05]
    maturities = [1, 2, 3]
    assert calculate_par_rate(spot_rates, maturities) == pytest.approx(0.05)

def test_calculate_par_rate_invalid_inputs():
    """Test par rate calculation with invalid inputs."""
    with pytest.raises(ValueError, match="Spot rates and maturities lists cannot be empty."):
        calculate_par_rate([], [])
    with pytest.raises(ValueError, match="Spot rates and maturities lists must have the same length."):
        calculate_par_rate([0.05], [1, 2])
    with pytest.raises(ValueError, match="Maturities must be positive."):
        calculate_par_rate([0.05, 0.06], [0, 2])
    with pytest.raises(ValueError, match="Maturities must be strictly increasing."):
        calculate_par_rate([0.05, 0.06], [1, 1])
    with pytest.raises(ValueError, match=r"Spot rates cannot be less than -1 \(or -100%\)\."):
        calculate_par_rate([-1.1, 0.06], [1, 2])
    
    # Test case for sum of discount factors being zero (unlikely in practice for real rates)
    # This might happen if maturities are extremely long and rates are extremely high.
    # For now, no direct test for this as it's hard to construct a simple input that hits this without extremely large numbers.

# --- bootstrap_yield_curve tests (conceptual/simplified) ---
def test_bootstrap_yield_curve_zero_coupon_bonds():
    """Test bootstrapping with simple zero-coupon bonds."""
    bond_data = [
        {'maturity_years': 0.5, 'coupon_rate': 0, 'face_value': 1000, 'market_price': 980.392, 'compounding_freq_per_year': 2}, # 4% annual
        {'maturity_years': 1.0, 'coupon_rate': 0, 'face_value': 1000, 'market_price': 961.169, 'compounding_freq_per_year': 2}, # 4.0% annual
    ]
    # Re-calculate expected values for 961.169 market price for 1 year, semi-annual (2 periods)
    # 1000 / (1+r/2)^2 = 961.169 => (1+r/2)^2 = 1000/961.169 => 1+r/2 = sqrt(1.0404) = 1.02
    # r/2 = 0.02 => r = 0.04
    expected_rates = {0.5: pytest.approx(0.04, rel=1e-4), 1.0: pytest.approx(0.04, rel=1e-4)}
    result = bootstrap_yield_curve(bond_data)
    for maturity, rate in expected_rates.items():
        assert result[maturity] == rate

def test_bootstrap_yield_curve_invalid_inputs():
    """Test bootstrap_yield_curve with invalid inputs."""
    with pytest.raises(ValueError, match="Bond data cannot be empty."):
        bootstrap_yield_curve([])
    with pytest.raises(ValueError, match="Market price for bond at .* years must be positive."):
        bootstrap_yield_curve([{'maturity_years': 1.0, 'coupon_rate': 0, 'face_value': 1000, 'market_price': 0, 'compounding_freq_per_year': 1}])
    with pytest.raises(ValueError, match="Compounding frequency for bond at .* years must be positive."):
        bootstrap_yield_curve([{'maturity_years': 1.0, 'coupon_rate': 0, 'face_value': 1000, 'market_price': 900, 'compounding_freq_per_year': 0}])
    with pytest.raises(ValueError, match="Zero maturity for zero-coupon bond at .* years."):
        bootstrap_yield_curve([{'maturity_years': 0, 'coupon_rate': 0, 'face_value': 1000, 'market_price': 900, 'compounding_freq_per_year': 1}])