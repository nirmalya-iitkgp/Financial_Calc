# tests/test_tvm.py

import pytest
import re # Import re for regex flags if needed (though we'll stick to exact matches)
import numpy_financial as npf # <--- ADD THIS LINE

from mathematical_functions.tvm import (
    calculate_fv_single_sum,
    calculate_pv_single_sum,
    calculate_fv_ordinary_annuity,
    calculate_pv_ordinary_annuity,
    calculate_loan_payment,
    convert_apr_to_ear
)
import math # Not directly used for assertions, but useful for calculating expected values

# --- calculate_fv_single_sum tests ---
def test_fv_single_sum_basic():
    """Test FV of a single sum with basic positive values."""
    assert calculate_fv_single_sum(100, 0.05, 1) == pytest.approx(105.0)
    assert calculate_fv_single_sum(1000, 0.10, 5) == pytest.approx(1610.51)

def test_fv_single_sum_zero_rate():
    """Test FV of a single sum with zero interest rate."""
    assert calculate_fv_single_sum(500, 0, 10) == pytest.approx(500.0)

def test_fv_single_sum_zero_periods():
    """Test FV of a single sum with zero periods."""
    assert calculate_fv_single_sum(1000, 0.08, 0) == pytest.approx(1000.0)

def test_fv_single_sum_negative_rate_valid():
    """Test FV of a single sum with a negative but valid rate (e.g., deflation)."""
    assert calculate_fv_single_sum(100, -0.05, 1) == pytest.approx(95.0)
    assert calculate_fv_single_sum(1000, -0.10, 2) == pytest.approx(810.0)

def test_fv_single_sum_invalid_n_periods():
    """Test FV of a single sum with invalid (negative) n_periods."""
    with pytest.raises(ValueError, match="Number of periods cannot be negative."):
        calculate_fv_single_sum(100, 0.05, -1)

def test_fv_single_sum_invalid_rate_below_neg_one():
    """Test FV of a single sum with invalid (below -1) rate."""
    with pytest.raises(ValueError, match="Rate cannot be less than -1 \\(or -100%\\)."): # Adjusted regex
        calculate_fv_single_sum(100, -1.1, 1)

# --- calculate_pv_single_sum tests ---
def test_pv_single_sum_basic():
    """Test PV of a single sum with basic positive values."""
    assert calculate_pv_single_sum(105, 0.05, 1) == pytest.approx(100.0)
    assert calculate_pv_single_sum(1610.51, 0.10, 5) == pytest.approx(1000.0)

def test_pv_single_sum_zero_rate():
    """Test PV of a single sum with zero discount rate."""
    assert calculate_pv_single_sum(500, 0, 10) == pytest.approx(500.0)

def test_pv_single_sum_zero_periods():
    """Test PV of a single sum with zero periods."""
    assert calculate_pv_single_sum(1000, 0.08, 0) == pytest.approx(1000.0)

def test_pv_single_sum_negative_rate_valid():
    """Test PV of a single sum with a negative but valid rate."""
    assert calculate_pv_single_sum(95, -0.05, 1) == pytest.approx(100.0)
    assert calculate_pv_single_sum(810, -0.10, 2) == pytest.approx(1000.0)

def test_pv_single_sum_invalid_n_periods():
    """Test PV of a single sum with invalid (negative) n_periods."""
    with pytest.raises(ValueError, match="Number of periods cannot be negative."):
        calculate_pv_single_sum(100, 0.05, -1)

def test_pv_single_sum_invalid_rate_below_neg_one():
    """Test PV of a single sum with invalid (below -1) rate."""
    with pytest.raises(ValueError, match="Rate cannot be less than -1 \\(or -100%\\)."): # Adjusted regex
        calculate_pv_single_sum(100, -1.1, 1)

# --- calculate_fv_ordinary_annuity tests ---
def test_fv_ordinary_annuity_basic():
    """Test FV of an ordinary annuity with basic values."""
    # FV of $100/yr for 3 years at 5%
    # Year 1: 100 * (1.05)^2 = 110.25
    # Year 2: 100 * (1.05)^1 = 105.00
    # Year 3: 100 * (1.05)^0 = 100.00
    # Total = 315.25
    assert calculate_fv_ordinary_annuity(100, 0.05, 3) == pytest.approx(315.25, rel=1e-6)
    assert calculate_fv_ordinary_annuity(500, 0.08, 10) == pytest.approx(7243.2753, rel=1e-6)

def test_fv_ordinary_annuity_zero_rate():
    """Test FV of an ordinary annuity with zero interest rate."""
    assert calculate_fv_ordinary_annuity(100, 0, 5) == pytest.approx(500.0)

def test_fv_ordinary_annuity_zero_periods():
    """Test FV of an ordinary annuity with zero periods."""
    # This test now passes because the tvm.py function correctly returns 0.0 for n_periods = 0.
    assert calculate_fv_ordinary_annuity(100, 0.05, 0) == pytest.approx(0.0)

def test_fv_ordinary_annuity_invalid_n_periods():
    """Test FV of an ordinary annuity with invalid (negative) n_periods."""
    # Regex updated to match the exact error message from the function
    with pytest.raises(ValueError, match="Number of periods cannot be negative."):
        calculate_fv_ordinary_annuity(100, 0.05, -1)

def test_fv_ordinary_annuity_invalid_rate_below_neg_one():
    """Test FV of an ordinary annuity with invalid (below -1) rate."""
    with pytest.raises(ValueError, match="Rate cannot be less than -1 \\(or -100%\\)."): # Adjusted regex
        calculate_fv_ordinary_annuity(100, -1.1, 1)

# --- calculate_pv_ordinary_annuity tests ---
def test_pv_ordinary_annuity_basic():
    """Test PV of an ordinary annuity with basic values."""
    # PV of $100/yr for 3 years at 5%
    # Year 1: 100 / (1.05)^1 = 95.238
    # Year 2: 100 / (1.05)^2 = 90.703
    # Year 3: 100 / (1.05)^3 = 86.384
    # Total = 272.325
    assert calculate_pv_ordinary_annuity(100, 0.05, 3) == pytest.approx(272.3248, rel=1e-6)
    assert calculate_pv_ordinary_annuity(500, 0.08, 10) == pytest.approx(3355.039, rel=1e-6)

def test_pv_ordinary_annuity_zero_rate():
    """Test PV of an ordinary annuity with zero discount rate."""
    assert calculate_pv_ordinary_annuity(100, 0, 5) == pytest.approx(500.0)

def test_pv_ordinary_annuity_zero_periods():
    """Test PV of an ordinary annuity with zero periods."""
    # This test now passes because the tvm.py function correctly returns 0.0 for n_periods = 0.
    assert calculate_pv_ordinary_annuity(100, 0.05, 0) == pytest.approx(0.0)

def test_pv_ordinary_annuity_invalid_n_periods():
    """Test PV of an ordinary annuity with invalid (negative) n_periods."""
    # Regex updated to match the exact error message from the function
    with pytest.raises(ValueError, match="Number of periods cannot be negative."):
        calculate_pv_ordinary_annuity(100, 0.05, -1)

def test_pv_ordinary_annuity_invalid_rate_below_neg_one():
    """Test PV of a single sum with invalid (below -1) rate."""
    with pytest.raises(ValueError, match="Rate cannot be less than -1 \\(or -100%\\)."): # Adjusted regex
        calculate_pv_ordinary_annuity(100, -1.1, 1)

# --- calculate_loan_payment tests ---
def test_loan_payment_basic_monthly():
    """Test loan payment for a basic monthly compounded loan."""
    # $100,000 loan, 5% annual, 30 years, monthly payments
    assert calculate_loan_payment(100000, 0.05, 30, 12) == pytest.approx(536.82, rel=1e-5) # Adjusted tolerance

def test_loan_payment_basic_annual():
    """Test loan payment for a basic annually compounded loan."""
    # $10,000 loan, 6% annual, 5 years, annual payments
    # Calculate expected value precisely for better comparison
    # pmt = pv * (rate * (1 + rate)**nper) / ((1 + rate)**nper - 1)
    # Using numpy_financial's own pmt calculation for the expected value
    expected_pmt = -npf.pmt(rate=0.06/1, nper=5*1, pv=10000) # npf is now imported
    assert calculate_loan_payment(10000, 0.06, 5, 1) == pytest.approx(expected_pmt, rel=1e-7) # Increased precision

def test_loan_payment_zero_rate():
    """Test loan payment with a zero interest rate."""
    # Should be principal / (n_years * compounding_freq_per_year)
    assert calculate_loan_payment(10000, 0, 10, 12) == pytest.approx(10000 / (10 * 12))

def test_loan_payment_invalid_principal():
    """Test loan payment with non-positive principal."""
    # Regex updated to match the exact error message from the function
    with pytest.raises(ValueError, match="Principal must be a positive value."):
        calculate_loan_payment(0, 0.05, 30, 12)
    with pytest.raises(ValueError, match="Principal must be a positive value."):
        calculate_loan_payment(-1000, 0.05, 30, 12)

def test_loan_payment_invalid_n_years():
    """Test loan payment with non-positive years."""
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_loan_payment(10000, 0.05, 0, 12)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_loan_payment(10000, 0.05, -5, 12)

def test_loan_payment_invalid_compounding_freq():
    """Test loan payment with non-positive compounding frequency."""
    with pytest.raises(ValueError, match="Compounding frequency must be positive."):
        calculate_loan_payment(10000, 0.05, 30, 0)
    with pytest.raises(ValueError, match="Compounding frequency must be positive."):
        calculate_loan_payment(10000, 0.05, 30, -4)

def test_loan_payment_invalid_annual_rate_below_neg_one():
    """Test loan payment with invalid (below -1) annual rate."""
    # Regex updated to match the exact error message from the function
    # Note: The function currently throws for *any* negative rate, not just below -1.
    with pytest.raises(ValueError, match="Annual rate cannot be negative."):
        calculate_loan_payment(10000, -1.1, 30, 12)

# --- convert_apr_to_ear tests ---
def test_convert_apr_to_ear_basic_monthly():
    """Test APR to EAR conversion for monthly compounding."""
    # 12% APR compounded monthly: (1 + 0.12/12)^12 - 1 = (1.01)^12 - 1 = 0.126825...
    expected_ear = (1 + (0.12 / 12)) ** 12 - 1
    assert convert_apr_to_ear(0.12, 12) == pytest.approx(expected_ear, rel=1e-7)

def test_convert_apr_to_ear_basic_quarterly():
    """Test APR to EAR conversion for quarterly compounding."""
    # 8% APR compounded quarterly: (1 + 0.08/4)^4 - 1 = (1.02)^4 - 1 = 0.082432...
    expected_ear = (1 + (0.08 / 4)) ** 4 - 1
    assert convert_apr_to_ear(0.08, 4) == pytest.approx(expected_ear, rel=1e-7)

def test_convert_apr_to_ear_annual_compounding():
    """Test APR to EAR conversion for annual compounding (should be same)."""
    assert convert_apr_to_ear(0.07, 1) == pytest.approx(0.07)

def test_convert_apr_to_ear_zero_apr():
    """Test APR to EAR conversion with zero APR."""
    assert convert_apr_to_ear(0, 12) == pytest.approx(0)

def test_convert_apr_to_ear_invalid_compounding_freq_zero():
    """Test APR to EAR conversion with invalid (zero) compounding frequency."""
    with pytest.raises(ValueError, match="Compounding frequency must be a positive integer."):
        convert_apr_to_ear(0.05, 0)

def test_convert_apr_to_ear_invalid_compounding_freq_negative():
    """Test APR to EAR conversion with invalid (negative) compounding frequency."""
    with pytest.raises(ValueError, match="Compounding frequency must be a positive integer."):
        convert_apr_to_ear(0.05, -4)

def test_convert_apr_to_ear_invalid_compounding_freq_float():
    """Test APR to EAR conversion with non-integer compounding frequency."""
    # This test now passes because the tvm.py function now checks for integer type.
    with pytest.raises(ValueError, match="Compounding frequency must be a positive integer."):
        convert_apr_to_ear(0.05, 2.5)

def test_convert_apr_to_ear_negative_apr_valid():
    """Test APR to EAR conversion with a negative but valid APR."""
    # -5% APR compounded annually: (1 + -0.05/1)^1 - 1 = -0.05
    assert convert_apr_to_ear(-0.05, 1) == pytest.approx(-0.05)
    # -5% APR compounded monthly: (1 + -0.05/12)^12 - 1
    expected_ear = (1 + (-0.05 / 12)) ** 12 - 1
    assert convert_apr_to_ear(-0.05, 12) == pytest.approx(expected_ear, rel=1e-7) # Adjusted to use exact calculation

def test_convert_apr_to_ear_invalid_apr_leads_to_negative_base():
    """Test APR to EAR conversion where 1 + rate/freq becomes negative."""
    # This test now passes because the tvm.py function now checks for (1 + periodic_rate) < 0.
    with pytest.raises(ValueError, match="Calculated periodic rate leads to \\(1 \\+ rate\\) < 0, which is invalid for real EAR."): # Adjusted regex for parentheses
        convert_apr_to_ear(-3.0, 2) # (1 + -3.0/2) = 1 - 1.5 = -0.5 (invalid base)
    
    # This case was initially listed as leading to error, but (1 + -1.5/2) = 0.25 is valid.
    # It should NOT raise an error based on the logic. If you want it to, adjust the threshold in tvm.py.
    # Keeping it here as a check that it *doesn't* raise an error.
    assert convert_apr_to_ear(-1.5, 2) == pytest.approx((1 + (-1.5/2))**2 - 1)