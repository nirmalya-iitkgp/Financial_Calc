# mathematical_functions/bonds.py

import numpy_financial as npf
import math

def calculate_bond_price(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the price of a coupon-paying bond.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal, e.g., 0.05 for 5%).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year
                                         (e.g., 2 for semi-annual, 4 for quarterly).

    Returns:
        float: The calculated price of the bond.

    Assumptions/Limitations:
    - Coupons are paid at the end of each compounding period (ordinary annuity).
    - Yield to maturity is constant throughout the life of the bond.
    - All inputs must be non-negative, except for coupon_rate which can be 0 for zero-coupon bonds.
    - Compounding frequency must be positive.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if coupon_rate < 0:
        raise ValueError("Coupon rate cannot be negative.")
    if yield_to_maturity < 0:
        raise ValueError("Yield to maturity cannot be negative.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be positive.")

    # Calculate periodic coupon payment and periodic yield
    periodic_coupon_payment = (coupon_rate * face_value) / compounding_freq_per_year
    periodic_yield = yield_to_maturity / compounding_freq_per_year
    total_periods = n_years * compounding_freq_per_year

    # Calculate present value of coupons (annuity)
    pv_coupons = -npf.pv(rate=periodic_yield, nper=total_periods, pmt=periodic_coupon_payment, fv=0, when='end')

    # Calculate present value of face value (lump sum at maturity)
    pv_face_value = -npf.pv(rate=periodic_yield, nper=total_periods, pmt=0, fv=face_value, when='end')

    # Bond price is the sum of the present value of coupons and the present value of the face value
    bond_price = pv_coupons + pv_face_value
    return bond_price

def calculate_zero_coupon_bond_price(face_value: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the price of a zero-coupon bond.

    Args:
        face_value (float): The par value or maturity value of the bond. Must be positive.
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded per year.

    Returns:
        float: The calculated price of the zero-coupon bond.

    Raises:
        ValueError: If inputs are invalid.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if yield_to_maturity < 0:
        raise ValueError("Yield to maturity cannot be negative.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be positive.")

    periodic_yield = yield_to_maturity / compounding_freq_per_year
    total_periods = n_years * compounding_freq_per_year

    # Price = FaceValue / (1 + periodic_yield)^total_periods
    # Use npf.pv for consistency
    # npf.pv expects fv to be positive for inflow, and will return negative for pv (initial outflow).
    # We want the positive price for the bond.
    bond_price = -npf.pv(rate=periodic_yield, nper=total_periods, pmt=0, fv=face_value)
    return bond_price


def calculate_zero_coupon_bond_yield(face_value: float, current_price: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the Yield to Maturity (YTM) for a zero-coupon bond.

    Args:
        face_value (float): The par value or maturity value of the bond. Must be positive.
        current_price (float): The current market price of the bond. Must be positive.
        n_years (float): The number of years until the bond matures. Must be positive.
        compounding_freq_per_year (int): Number of times interest is compounded per year. Must be positive.

    Returns:
        float: The calculated annual yield to maturity (as a decimal).

    Assumptions/Limitations:
    - Zero-coupon bond.
    - current_price must be positive and typically less than face_value for a positive yield.
    - All inputs must be positive.
    """
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if current_price <= 0:
        raise ValueError("Current price must be positive.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be positive.")

    # A bond trading above face value implies a negative yield to maturity.
    # This is mathematically possible.
    
    total_periods = n_years * compounding_freq_per_year

    # Formula: Price = FaceValue / (1 + periodic_yield)^total_periods
    # Rearranging for periodic_yield:
    # (1 + periodic_yield)^total_periods = FaceValue / Price
    # 1 + periodic_yield = (FaceValue / Price)^(1 / total_periods)
    # periodic_yield = (FaceValue / Price)^(1 / total_periods) - 1

    periodic_yield = (face_value / current_price)**(1 / total_periods) - 1
    annual_yield = periodic_yield * compounding_freq_per_year
    return annual_yield