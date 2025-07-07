# mathematical_functions/capital_budgeting.py

import math
import numpy as np
import numpy_financial as npf # We will use this for NPV and IRR calculations

def calculate_payback_period(initial_investment: float, cash_flows: list[float]) -> float:
    """
    Calculates the Payback Period for an investment.
    The payback period is the time required for an investment to generate cash flows
    sufficient to recover its initial cost.

    Args:
        initial_investment (float): The initial cash outflow (e.g., -10000). Should be a negative number.
        cash_flows (list[float]): A list of positive cash inflows for each period (e.g., [3000, 4000, 5000]).
                                  Assumes cash flows occur at the end of each period.

    Returns:
        float: The payback period in units of the periods used for cash flows (e.g., years).
               Returns float('inf') if the initial investment is never recovered.

    Raises:
        ValueError: If initial_investment is not negative, if cash_flows is empty or contains non-positive values.

    Assumptions/Limitations:
    - Ignores the time value of money.
    - Cash flows are assumed to be evenly spread within the period for fractional calculations.
    - Does not consider cash flows beyond the payback period.
    """
    if initial_investment >= 0:
        raise ValueError("Initial investment must be a negative value representing an outflow.")
    if not cash_flows:
        raise ValueError("Cash flows list cannot be empty.")
    if any(cf <= 0 for cf in cash_flows):
        raise ValueError("All cash flows (inflows) must be positive.")

    remaining_investment = abs(initial_investment) # Work with positive value for recovery
    payback_period = 0.0

    for i, cf in enumerate(cash_flows):
        if remaining_investment <= 0:
            break # Investment already recovered in a previous full period

        if remaining_investment > cf:
            remaining_investment -= cf
            payback_period += 1
        else:
            # Investment recovered within this period
            payback_period += remaining_investment / cf
            remaining_investment = 0 # Fully recovered
            break
    
    if remaining_investment > 0:
        return float('inf') # Initial investment not fully recovered
    else:
        return payback_period

def calculate_discounted_payback_period(initial_investment: float, cash_flows: list[float], discount_rate: float) -> float:
    """
    Calculates the Discounted Payback Period for an investment.
    This is similar to the payback period but uses discounted cash flows,
    thus considering the time value of money.

    Args:
        initial_investment (float): The initial cash outflow (e.g., -10000). Should be a negative number.
        cash_flows (list[float]): A list of positive cash inflows for each period.
                                  Assumes cash flows occur at the end of each period.
        discount_rate (float): The discount rate per period (as a decimal, e.g., 0.10 for 10%).
                               Must be non-negative.

    Returns:
        float: The discounted payback period in units of the periods used for cash flows.
               Returns float('inf') if the initial investment is never recovered from discounted cash flows.

    Raises:
        ValueError: If initial_investment is not negative, if cash_flows is empty or contains non-positive values,
                    or if discount_rate is negative.

    Assumptions/Limitations:
    - Considers the time value of money by discounting cash flows.
    - Cash flows are assumed to be evenly spread within the period for fractional calculations.
    - Does not consider cash flows beyond the discounted payback period.
    """
    if initial_investment >= 0:
        raise ValueError("Initial investment must be a negative value representing an outflow.")
    if not cash_flows:
        raise ValueError("Cash flows list cannot be empty.")
    if any(cf <= 0 for cf in cash_flows):
        raise ValueError("All cash flows (inflows) must be positive.")
    if discount_rate < 0:
        raise ValueError("Discount rate cannot be negative.")

    remaining_investment = abs(initial_investment)
    discounted_payback_period = 0.0
    cumulative_discounted_cash_flow = 0.0

    for i, cf in enumerate(cash_flows):
        # Period is i+1 (1-based)
        discount_factor = 1 / ((1 + discount_rate)**(i + 1))
        discounted_cf = cf * discount_factor
        
        # Check if current cumulative discounted cash flow has already covered initial investment
        # before adding this period's cash flow. This handles edge cases where a previous period fully recovers.
        if cumulative_discounted_cash_flow >= abs(initial_investment):
            break

        if (cumulative_discounted_cash_flow + discounted_cf) < abs(initial_investment):
            cumulative_discounted_cash_flow += discounted_cf
            discounted_payback_period += 1
        else:
            # Investment recovered within this period
            amount_needed = abs(initial_investment) - cumulative_discounted_cash_flow
            discounted_payback_period += amount_needed / discounted_cf
            cumulative_discounted_cash_flow = abs(initial_investment) # Fully recovered
            break
    
    if cumulative_discounted_cash_flow < abs(initial_investment):
        return float('inf') # Initial investment not fully recovered
    else:
        return discounted_payback_period

def calculate_npv(rate: float, cash_flows: list[float]) -> float:
    """
    Calculates the Net Present Value (NPV) of a series of cash flows.
    NPV is the difference between the present value of cash inflows and the present
    value of cash outflows over a period of time.

    Args:
        rate (float): The discount rate per period (as a decimal, e.g., 0.10 for 10%).
                      Must be greater than -1.
        cash_flows (list[float]): A list of cash flows, where the first element is the
                                  initial investment (a negative value) and subsequent
                                  elements are future cash inflows/outflows.
                                  (e.g., [-10000, 3000, 4000, 5000]).

    Returns:
        float: The calculated Net Present Value.

    Raises:
        ValueError: If cash_flows is empty, or if rate is less than or equal to -1.

    Assumptions/Limitations:
    - Cash flows occur at the end of each period.
    - The discount rate remains constant over the life of the project.
    - Reinvestment of intermediate cash flows occurs at the discount rate.
    """
    if not cash_flows:
        raise ValueError("Cash flows list cannot be empty.")
    if rate <= -1:
        raise ValueError("The discount rate (rate) must be greater than -1 (or -100%).")
    
    # numpy_financial.npv expects the initial investment to be part of the cash_flows list.
    # The first cash flow in the list is discounted as if it occurs at time 0 (no discount),
    # subsequent cash flows are discounted from period 1, 2, ...
    # This is exactly what we need for NPV where the first element is usually the initial investment.
    return npf.npv(rate, cash_flows)

def calculate_irr(cash_flows: list[float]) -> float:
    """
    Calculates the Internal Rate of Return (IRR) for a series of cash flows.
    IRR is the discount rate that makes the Net Present Value (NPV) of all cash flows
    from a particular project equal to zero.

    Args:
        cash_flows (list[float]): A list of cash flows, where the first element is the
                                  initial investment (a negative value) and subsequent
                                  elements are future cash inflows/outflows.
                                  (e.g., [-10000, 3000, 4000, 5000]).
                                  Must contain at least one positive and one negative cash flow.

    Returns:
        float: The calculated Internal Rate of Return as a decimal.

    Raises:
        ValueError: If cash_flows is empty, or if it does not contain at least one positive
                    and one negative value (IRR is undefined in such cases).
                    Also, if the IRR calculation does not converge.

    Assumptions/Limitations:
    - Assumes that cash flows occur at the end of each period.
    - Assumes reinvestment of intermediate cash flows at the IRR.
    - Multiple IRRs can exist if cash flows change sign more than once. This function returns
      only one (the first one found by the numerical solver).
    - May not converge for all cash flow streams.
    """
    if not cash_flows:
        raise ValueError("Cash flows list cannot be empty.")
    
    # Check if there's at least one positive and one negative cash flow for IRR to be meaningful
    has_positive = any(cf > 0 for cf in cash_flows)
    has_negative = any(cf < 0 for cf in cash_flows)
    if not (has_positive and has_negative):
        raise ValueError("Cash flows must contain at least one positive and one negative value for IRR calculation.")

    try:
        return npf.irr(cash_flows)
    except ValueError: # numpy_financial raises ValueError if IRR doesn't converge
        raise ValueError("IRR calculation did not converge. Ensure valid cash flow stream.")

def calculate_profitability_index(initial_investment: float, cash_flows: list[float], discount_rate: float) -> float:
    """
    Calculates the Profitability Index (PI) of an investment.
    The PI is the ratio of the present value of future cash inflows to the initial investment.
    A PI greater than 1.0 generally indicates an acceptable investment.

    Formula: PI = (Present Value of Future Cash Inflows) / |Initial Investment|
    OR: PI = (NPV + |Initial Investment|) / |Initial Investment|

    Args:
        initial_investment (float): The initial cash outflow (e.g., -10000). Should be a negative number.
        cash_flows (list[float]): A list of future cash inflows/outflows after the initial investment.
                                  (e.g., [3000, 4000, 5000]). These should NOT include the initial investment.
        discount_rate (float): The discount rate per period (as a decimal, e.g., 0.10 for 10%).
                               Must be greater than -1.

    Returns:
        float: The calculated Profitability Index.

    Raises:
        ValueError: If initial_investment is not negative, if cash_flows is empty,
                    if discount_rate is less than or equal to -1, or if initial_investment is zero.

    Assumptions/Limitations:
    - Cash flows occur at the end of each period.
    - Requires future cash flows to be separate from the initial investment for calculation.
    """
    if initial_investment >= 0:
        raise ValueError("Initial investment must be a negative value representing an outflow.")
    if not cash_flows:
        raise ValueError("Future cash flows list cannot be empty.")
    if discount_rate <= -1:
        raise ValueError("The discount rate (rate) must be greater than -1 (or -100%).")
    if math.isclose(initial_investment, 0.0, abs_tol=1e-9):
        raise ValueError("Initial investment cannot be zero for Profitability Index calculation.")

    # Calculate Present Value of Future Cash Inflows
    # We create a temporary cash flow list for npf.npv where the first element is 0
    # and subsequent elements are the future cash flows, to get only the PV of future C.F.
    # npf.npv(rate, [0, CF1, CF2, ...]) gives PV(CF1) + PV(CF2) + ...
    pv_future_cash_flows = npf.npv(discount_rate, [0] + cash_flows)
    
    profitability_index = pv_future_cash_flows / abs(initial_investment)
    return profitability_index