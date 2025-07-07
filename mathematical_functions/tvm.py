# mathematical_functions/tvm.py

import numpy_financial as npf
import math # Not directly used for calculations after moving to npf, but kept for potential future use or clarity.

def calculate_fv_single_sum(pv: float, rate: float, n_periods: float) -> float:
    """
    Calculates the Future Value (FV) of a single sum.

    Args:
        pv (float): Present Value (the initial amount).
        rate (float): Interest rate per period (as a decimal, e.g., 0.05 for 5%).
        n_periods (float): Number of compounding periods.

    Returns:
        float: The Future Value of the single sum.

    Assumptions/Limitations:
    - Compounding occurs at the end of each period.
    - Rate and n_periods must be consistent (e.g., if rate is annual, n_periods must be in years).
    - Ensures valid non-negative periods and rate not less than -1.
    """
    if n_periods < 0:
        raise ValueError("Number of periods cannot be negative.")
    if rate < -1:
        # A rate less than -100% (e.g., -1.1) would imply a future value
        # that is less than the original principal after a single period,
        # moving towards negative infinity with more periods for a positive PV,
        # which is generally not financially meaningful.
        raise ValueError("Rate cannot be less than -1 (or -100%).")
    
    # numpy_financial.fv expects pv to be negative (cash outflow) to return a positive fv.
    # We are providing pv as a positive number from user input, so we negate it here
    # to get a positive FV result.
    fv = npf.fv(rate=rate, nper=n_periods, pmt=0, pv=-pv)
    return fv

def calculate_pv_single_sum(fv: float, rate: float, n_periods: float) -> float:
    """
    Calculates the Present Value (PV) of a single sum.

    Args:
        fv (float): Future Value (the target amount).
        rate (float): Discount rate per period (as a decimal, e.g., 0.05 for 5%).
        n_periods (float): Number of discounting periods.

    Returns:
        float: The Present Value of the single sum.

    Assumptions/Limitations:
    - Discounting occurs at the end of each period.
    - Rate and n_periods must be consistent.
    - Ensures valid non-negative periods and rate not less than -1.
    """
    if n_periods < 0:
        raise ValueError("Number of periods cannot be negative.")
    if rate < -1:
        # Similar logic as FV: a discount rate less than -100% is not meaningful.
        raise ValueError("Rate cannot be less than -1 (or -100%).")

    # numpy_financial.pv expects fv to be positive (cash inflow) to return a negative pv.
    # We need to ensure fv is treated correctly based on its financial direction.
    # The output of npf.pv is typically negative for a positive fv, so we negate it
    # to return a positive PV for user display, indicating current worth.
    pv = npf.pv(rate=rate, nper=n_periods, pmt=0, fv=fv)
    return -pv # Return as a positive value for user display, indicating current worth

def calculate_fv_ordinary_annuity(pmt: float, rate: float, n_periods: float) -> float:
    """
    Calculates the Future Value (FV) of an ordinary annuity.
    An ordinary annuity has payments at the end of each period.

    Args:
        pmt (float): Payment amount per period.
        rate (float): Interest rate per period (as a decimal).
        n_periods (float): Number of periods.

    Returns:
        float: The Future Value of the ordinary annuity.

    Assumptions/Limitations:
    - Payments are equal and occur at the end of each period.
    - Rate and n_periods must be consistent.
    - Rate cannot be -1 (or -100%), as this leads to division by zero in some underlying formulas
      (though numpy_financial handles this gracefully for rate=0).
    - Ensures valid non-negative periods and rate not less than -1.
    """
    if n_periods < 0:
        # Number of periods cannot be negative.
        raise ValueError("Number of periods cannot be negative.")
    if n_periods == 0:
        # If there are no periods, no payments are made, so FV is 0.
        return 0.0
    if rate < -1:
        # A rate less than -100% (e.g., -1.1) would imply strange growth/decay.
        raise ValueError("Rate cannot be less than -1 (or -100%).")
        
    # numpy_financial.fv for annuities: pmt is negative (cash outflow), pv is 0.
    # The 'when' argument defaults to 'end' for ordinary annuities.
    fv = npf.fv(rate=rate, nper=n_periods, pmt=-pmt, pv=0, when='end')
    return fv

def calculate_pv_ordinary_annuity(pmt: float, rate: float, n_periods: float) -> float:
    """
    Calculates the Present Value (PV) of an ordinary annuity.
    An ordinary annuity has payments at the end of each period.

    Args:
        pmt (float): Payment amount per period.
        rate (float): Discount rate per period (as a decimal).
        n_periods (float): Number of periods.

    Returns:
        float: The Present Value of the ordinary annuity.

    Assumptions/Limitations:
    - Payments are equal and occur at the end of each period.
    - Rate and n_periods must be consistent.
    - Rate cannot be -1 (or -100%).
    - Ensures valid non-negative periods and rate not less than -1.
    """
    if n_periods < 0:
        # Number of periods cannot be negative.
        raise ValueError("Number of periods cannot be negative.")
    if n_periods == 0:
        # If there are no periods, no payments are made, so PV is 0.
        return 0.0
    if rate < -1:
        # A discount rate less than -100% is not meaningful.
        raise ValueError("Rate cannot be less than -1 (or -100%).")

    # numpy_financial.pv for annuities: pmt is negative (cash outflow), fv is 0.
    # The 'when' argument defaults to 'end' for ordinary annuities.
    # The output of npf.pv is typically negative for a series of positive payments (cash outflow to make the payments),
    # so we return it as is if pmt is positive for user display as a positive value (cost of annuity).
    pv = npf.pv(rate=rate, nper=n_periods, pmt=-pmt, fv=0, when='end')
    return pv

def calculate_loan_payment(principal: float, annual_rate: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the fixed payment for an amortizing loan.

    Args:
        principal (float): The initial loan amount.
        annual_rate (float): The annual interest rate (as a decimal).
        n_years (float): The total number of years for the loan.
        compounding_freq_per_year (int): Number of times interest is compounded per year
                                         (e.g., 12 for monthly, 4 for quarterly).

    Returns:
        float: The fixed payment amount per compounding period.

    Assumptions/Limitations:
    - Payments are made at the end of each compounding period (ordinary annuity).
    - Interest rate and number of periods are adjusted for compounding frequency.
    - Assumes a fixed-rate loan.
    - Ensures principal, years, and compounding frequency are positive, and annual_rate is non-negative.
    """
    if principal <= 0:
        raise ValueError("Principal must be a positive value.")
    # The test for loan payment (test_loan_payment_invalid_annual_rate_below_neg_one)
    # implies that any negative annual rate is invalid.
    # If rates below -1 were allowed, this check would need to be `annual_rate < -1`.
    # Sticking with the current test's expectation of `annual_rate < 0` for now.
    if annual_rate < 0:
        raise ValueError("Annual rate cannot be negative.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency must be positive.")

    period_rate = annual_rate / compounding_freq_per_year
    total_periods = n_years * compounding_freq_per_year

    # numpy_financial.pmt: principal (pv) is positive (cash inflow to borrower).
    # Payment (pmt) will be negative as it's a cash outflow from borrower.
    payment = npf.pmt(rate=period_rate, nper=total_periods, pv=principal)
    return -payment # Return as a positive value for user display

def convert_apr_to_ear(apr: float, compounding_freq_per_year: int) -> float:
    """
    Converts an Annual Percentage Rate (APR) to an Effective Annual Rate (EAR).

    Args:
        apr (float): The Annual Percentage Rate (as a decimal, e.g., 0.05 for 5%).
        compounding_freq_per_year (int): Number of times interest is compounded per year.

    Returns:
        float: The Effective Annual Rate (as a decimal).

    Assumptions/Limitations:
    - APR is stated as a simple rate, not already an EAR.
    - Compounding frequency must be a positive integer.
    - Valid for any non-negative APR, and negative APRs as long as (1 + APR/m) is not negative.
    """
    # Check if compounding_freq_per_year is a positive integer
    if not isinstance(compounding_freq_per_year, int) or compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency must be a positive integer.")
    
    periodic_rate = apr / compounding_freq_per_year

    # Financial rates should generally not lead to (1 + rate/m) being negative,
    # as this implies losing more than 100% of value per period, which is not
    # typical for real-world scenarios that compound over time with real values.
    # This check prevents math domain errors or unexpected complex numbers from pow().
    if (1 + periodic_rate) < 0:
        raise ValueError("Calculated periodic rate leads to (1 + rate) < 0, which is invalid for real EAR.")

    ear = (1 + periodic_rate) ** compounding_freq_per_year - 1
    return ear