# mathematical_functions/bond_risk.py

import math
import numpy as np

def _calculate_macaulay_duration_helper(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    (HELPER FUNCTION)
    Calculates the Macaulay Duration of a coupon-paying bond.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year.

    Returns:
        float: The Macaulay Duration of the bond in years.

    Raises:
        ValueError: If inputs are invalid.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if not (0 <= coupon_rate <= 1):
        raise ValueError("Coupon rate must be between 0 and 1 (as a decimal).")
    if yield_to_maturity < -1:
        raise ValueError("Yield to maturity cannot be less than -1 (or -100%).")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if not isinstance(compounding_freq_per_year, int) or compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be a positive integer.")

    periodic_coupon_rate = coupon_rate / compounding_freq_per_year
    periodic_yield = yield_to_maturity / compounding_freq_per_year

    # ADD THIS CHECK:
    if (1 + periodic_yield) <= 0:
        raise ValueError("Periodic yield leads to a discount factor of zero or negative, making Macaulay Duration undefined.")

    total_periods = int(n_years * compounding_freq_per_year)

    if total_periods == 0:
        return 0.0

    coupon_payment = face_value * periodic_coupon_rate

    # Calculate bond price (PV of all cash flows) and weighted time in a consistent loop
    calculated_bond_price = 0.0
    weighted_time_cash_flows = 0.0

    for t in range(1, total_periods + 1):
        cash_flow = coupon_payment
        if t == total_periods:
            cash_flow += face_value

        # Present value of each cash flow
        pv_cf_t = cash_flow / ((1 + periodic_yield)**t)
        
        calculated_bond_price += pv_cf_t
        weighted_time_cash_flows += pv_cf_t * t

    if calculated_bond_price <= 0:
        raise ValueError("Calculated bond price is zero or negative, Macaulay Duration cannot be calculated.")

    macaulay_duration = (weighted_time_cash_flows / calculated_bond_price) / compounding_freq_per_year
    return macaulay_duration


def calculate_modified_duration(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the Modified Duration of a coupon-paying bond.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year.

    Returns:
        float: The Modified Duration of the bond in years.

    Raises:
        ValueError: If inputs are invalid or lead to undefined duration.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if yield_to_maturity < -1:
        raise ValueError("Yield to maturity cannot be less than -1 (or -100%).")
    if compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be positive.")

    macaulay_duration = _calculate_macaulay_duration_helper(face_value, coupon_rate, yield_to_maturity, n_years, compounding_freq_per_year)

    if (1 + yield_to_maturity / compounding_freq_per_year) == 0:
        raise ValueError("Denominator for Modified Duration calculation is zero, leading to an undefined result.")
        
    modified_duration = macaulay_duration / (1 + (yield_to_maturity / compounding_freq_per_year))
    return modified_duration

def calculate_convexity(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the Convexity of a coupon-paying bond.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year.

    Returns:
        float: The Convexity of the bond.

    Raises:
        ValueError: If inputs are invalid.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if not (0 <= coupon_rate <= 1):
        raise ValueError("Coupon rate must be between 0 and 1 (as a decimal).")
    if yield_to_maturity < -1:
        raise ValueError("Yield to maturity cannot be less than -1 (or -100%).")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if not isinstance(compounding_freq_per_year, int) or compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be a positive integer.")

    periodic_coupon_rate = coupon_rate / compounding_freq_per_year
    periodic_yield = yield_to_maturity / compounding_freq_per_year
    total_periods = int(n_years * compounding_freq_per_year)

    if total_periods == 0:
        return 0.0

    if (1 + periodic_yield) <= 0:
        raise ValueError("Yield to maturity leads to an invalid periodic yield for calculation (1 + periodic_yield must be positive).")

    coupon_payment = face_value * periodic_coupon_rate

    calculated_bond_price = 0.0
    sum_pv_time_sq_plus_time = 0.0

    for t in range(1, total_periods + 1):
        cash_flow = coupon_payment
        if t == total_periods:
            cash_flow += face_value
        
        pv_cf_t = cash_flow / ((1 + periodic_yield)**t)
        calculated_bond_price += pv_cf_t
        sum_pv_time_sq_plus_time += cash_flow * t * (t + 1) / ((1 + periodic_yield)**t)

    if calculated_bond_price <= 0:
        raise ValueError("Bond price is zero or negative, convexity cannot be calculated.")

    convexity = sum_pv_time_sq_plus_time / (calculated_bond_price * (1 + periodic_yield)**2 * (compounding_freq_per_year**2))
    
    return convexity