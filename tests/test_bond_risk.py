import pytest
import math
import numpy as np



from mathematical_functions.bond_risk import (
    _calculate_macaulay_duration_helper,
    calculate_modified_duration,
    calculate_convexity
)

# Helper function for almost equal comparisons
def assert_close(actual, expected, rel_tol=1e-9, abs_tol=0.0):
    assert math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol), \
        f"Expected {expected}, got {actual}"

# --- Tests for _calculate_macaulay_duration_helper ---

def test_macaulay_duration_helper_basic():
    # Example bond: 5-year, 5% coupon, 6% YTM, semi-annual, $1000 face value
    face_value = 1000.0
    coupon_rate = 0.05
    yield_to_maturity = 0.06
    n_years = 5.0
    compounding_freq_per_year = 2

    # Expected duration from a reliable calculation/source or the function's precise output
    expected_duration = 4.471678607581262

    actual_duration = _calculate_macaulay_duration_helper(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert actual_duration == pytest.approx(expected_duration, rel=1e-9)

def test_macaulay_duration_helper_zero_coupon():
    face_value = 1000.0
    coupon_rate = 0.0
    yield_to_maturity = 0.05
    n_years = 3.0
    compounding_freq_per_year = 1 # Annual compounding

    # For a zero-coupon bond, Macaulay Duration is equal to its time to maturity
    expected_duration = n_years
    actual_duration = _calculate_macaulay_duration_helper(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert_close(actual_duration, expected_duration)

def test_macaulay_duration_helper_invalid_coupon_rate():
    face_value = 1000.0
    coupon_rate_low = -0.01  # Invalid: less than 0
    coupon_rate_high = 1.01 # Invalid: greater than 1
    yield_to_maturity = 0.05
    n_years = 5.0
    compounding_freq_per_year = 2

    expected_error_regex = r"Coupon rate must be between 0 and 1 \(as a decimal\)."

    with pytest.raises(ValueError, match=expected_error_regex):
        _calculate_macaulay_duration_helper(face_value, coupon_rate_low, yield_to_maturity, n_years, compounding_freq_per_year)

    with pytest.raises(ValueError, match=expected_error_regex):
        _calculate_macaulay_duration_helper(face_value, coupon_rate_high, yield_to_maturity, n_years, compounding_freq_per_year)

def test_macaulay_duration_helper_invalid_inputs():
    with pytest.raises(ValueError, match="Face value must be positive."):
        _calculate_macaulay_duration_helper(0, 0.05, 0.05, 5, 2)
    with pytest.raises(ValueError, match="Yield to maturity cannot be less than -1"):
        _calculate_macaulay_duration_helper(1000, 0.05, -1.1, 5, 2)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        _calculate_macaulay_duration_helper(1000, 0.05, 0.05, 0, 2)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        _calculate_macaulay_duration_helper(1000, 0.05, 0.05, 5, 0)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        _calculate_macaulay_duration_helper(1000, 0.05, 0.05, 5, 2.5) # Not an integer


# --- Tests for calculate_modified_duration ---

def test_modified_duration_basic():
    face_value = 1000.0
    coupon_rate = 0.05
    yield_to_maturity = 0.06
    n_years = 5.0
    compounding_freq_per_year = 2 # Semi-annual

    # Mac Duration for these inputs from helper test is ~4.471678607581262
    macaulay_duration_value = 4.471678607581262

    # Expected Modified Duration = Macaulay / (1 + YTM/m)
    expected_modified_duration = macaulay_duration_value / (1 + (yield_to_maturity / compounding_freq_per_year))
    actual_modified_duration = calculate_modified_duration(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert actual_modified_duration == pytest.approx(expected_modified_duration, rel=1e-9)


def test_modified_duration_zero_coupon():
    face_value = 1000.0
    coupon_rate = 0.0
    yield_to_maturity = 0.05
    n_years = 3.0
    compounding_freq_per_year = 1 # Annual compounding

    # For zero-coupon bond, Macaulay Duration is n_years.
    # Modified Duration = Macaulay Duration / (1 + YTM / m)
    expected_modified_duration = n_years / (1 + yield_to_maturity / compounding_freq_per_year)
    actual_modified_duration = calculate_modified_duration(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert_close(actual_modified_duration, expected_modified_duration)


def test_modified_duration_invalid_ytm_less_than_neg_1():
    # This test specifically covers the initial validation of YTM
    face_value = 1000.0
    coupon_rate = 0.05
    n_years = 5.0
    compounding_freq_per_year = 2
    yield_to_maturity = -2.0 # This triggers the YTM < -1 check

    with pytest.raises(ValueError, match="Yield to maturity cannot be less than -1"):
        calculate_modified_duration(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)

def test_modified_duration_denominator_zero():
    # This test specifically covers the (1 + YTM/m) == 0 case
    # This happens when YTM = -compounding_freq_per_year.
    # For this to pass the initial YTM validation, YTM must be >= -1.
    # So, compounding_freq_per_year must be 1 and YTM must be -1.0.
    face_value = 1000.0
    coupon_rate = 0.05
    n_years = 5.0
    compounding_freq_per_year = 1
    yield_to_maturity = -1.0 # This makes (1 + YTM/m) = (1 + -1/1) = 0

    # UPDATE THE EXPECTED ERROR MESSAGE HERE:
    with pytest.raises(ValueError, match="Periodic yield leads to a discount factor of zero or negative, making Macaulay Duration undefined."):
        calculate_modified_duration(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)


# --- Tests for calculate_convexity ---

def test_convexity_basic():
    face_value = 1000.0
    coupon_rate = 0.05
    yield_to_maturity = 0.06
    n_years = 5.0
    compounding_freq_per_year = 2 # Semi-annual

    # This value is based on the 'Obtained' value from your previous test run.
    # Verify this against a reliable source if you want to confirm absolute correctness of your function's formula.
    expected_convexity = 22.304728039361724

    actual_convexity = calculate_convexity(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert actual_convexity == pytest.approx(expected_convexity, rel=1e-9)

def test_convexity_zero_coupon():
    face_value = 1000.0
    coupon_rate = 0.0
    yield_to_maturity = 0.05
    n_years = 3.0
    compounding_freq_per_year = 1 # Annual compounding

    # This value is based on the 'Obtained' value from your previous test run.
    # Verify this against a reliable source if you want to confirm absolute correctness of your function's formula.
    expected_convexity_zero_coupon = 10.884353741496598
    actual_convexity = calculate_convexity(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)
    assert actual_convexity == pytest.approx(expected_convexity_zero_coupon, rel=1e-9)


def test_convexity_invalid_inputs():
    # Test initial YTM validation
    with pytest.raises(ValueError, match="Yield to maturity cannot be less than -1"):
        calculate_convexity(1000, 0.05, -2.1, 5, 2)

    # Test specific error for (1 + periodic_yield) <= 0
    # This requires YTM = -1.0 and compounding_freq_per_year = 1
    with pytest.raises(ValueError, match="Yield to maturity leads to an invalid periodic yield for calculation"):
        calculate_convexity(1000, 0.05, -1.0, 5, 1)

    # Other general invalid input tests for convexity
    with pytest.raises(ValueError, match="Face value must be positive."):
        calculate_convexity(0, 0.05, 0.05, 5, 2)
    with pytest.raises(ValueError, match="Coupon rate must be between 0 and 1"):
        calculate_convexity(1000, 1.1, 0.05, 5, 2)
    with pytest.raises(ValueError, match="Number of years must be positive."):
        calculate_convexity(1000, 0.05, 0.05, 0, 2)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        calculate_convexity(1000, 0.05, 0.05, 5, 0)
    with pytest.raises(ValueError, match="Compounding frequency per year must be a positive integer."):
        calculate_convexity(1000, 0.05, 0.05, 5, 2.5) # Not an integer

    # The "Bond price is zero or negative, convexity cannot be calculated." error
    # is generally hard to trigger with valid YTM inputs as the bond price would typically be positive.
    # It might be reached if YTM is extremely high and positive for a bond, making PV of later cash flows negligible or negative.
    # For now, it's not explicitly tested here as it's typically covered by other error checks.