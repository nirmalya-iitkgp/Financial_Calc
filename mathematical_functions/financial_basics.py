# mathematical_functions/financial_basics.py

import math

def calculate_perpetuity(payment: float, rate: float) -> float:
    """
    Calculates the present value of a perpetuity.
    A perpetuity is a stream of equal payments that continues indefinitely.

    Args:
        payment (float): The constant payment received or paid per period.
        rate (float): The discount rate per period (as a decimal).

    Returns:
        float: The Present Value of the perpetuity.

    Assumptions/Limitations:
    - Payments are equal and occur at the end of each period, continuing forever.
    - The discount rate (rate) is constant.
    - Rate must be greater than 0 to avoid division by zero and ensure a finite value.
    - Payment can be positive (inflow) or negative (outflow).
    """
    if rate <= 0:
        raise ValueError("The discount rate (rate) for a perpetuity must be greater than 0.")
    
    perpetuity_value = payment / rate
    return perpetuity_value

def calculate_growing_perpetuity(payment_year1: float, rate: float, growth_rate: float) -> float:
    """
    Calculates the present value of a growing perpetuity.
    A growing perpetuity is a stream of payments that grows at a constant rate forever.

    Args:
        payment_year1 (float): The payment expected at the end of the first period.
        rate (float): The discount rate per period (as a decimal).
        growth_rate (float): The constant growth rate of the payment per period (as a decimal).

    Returns:
        float: The Present Value of the growing perpetuity.

    Assumptions/Limitations:
    - Payments grow at a constant rate and occur at the end of each period, continuing forever.
    - The discount rate (rate) is constant.
    - The discount rate (rate) must be strictly greater than the growth rate (growth_rate)
      to ensure a finite and meaningful value.
    - payment_year1 can be positive or negative.
    """
    if rate <= growth_rate:
        raise ValueError("The discount rate (rate) must be strictly greater than the growth rate (growth_rate) for a growing perpetuity.")
    
    growing_perpetuity_value = payment_year1 / (rate - growth_rate)
    return growing_perpetuity_value