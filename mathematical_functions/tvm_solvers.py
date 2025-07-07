# mathematical_functions/tvm_solvers.py

import numpy_financial as npf
import numpy as np # Used for array operations and potentially more advanced numerical tasks
import scipy.optimize as optimize # For iterative solvers like IRR if numpy_financial isn't sufficient

def calculate_npv(rate: float, cash_flows: list[float]) -> float:
    """
    Calculates the Net Present Value (NPV) of a series of uneven cash flows.

    Args:
        rate (float): The discount rate per period (as a decimal, e.g., 0.05 for 5%).
                      This rate is assumed to be consistent with the periodicity of cash_flows.
        cash_flows (list[float]): A list of cash flows, where the first element
                                  (index 0) is typically the initial investment (a negative value),
                                  followed by subsequent positive or negative cash flows.

    Returns:
        float: The Net Present Value.

    Assumptions/Limitations:
    - Cash flows occur at the end of each period.
    - The discount rate (rate) is constant over all periods.
    - An empty cash_flows list or a rate less than -1 will raise a ValueError.
    """
    if not cash_flows:
        raise ValueError("Cash flows list cannot be empty.")
    if rate < -1:
        raise ValueError("Rate cannot be less than -1 (or -100%).")
    
    # numpy_financial.npv handles the discounting and summation directly.
    # It assumes cash_flows[0] is at time 0, cash_flows[1] at time 1, etc.
    npv = npf.npv(rate=rate, values=cash_flows)
    return npv

def calculate_irr(cash_flows: list[float]) -> float:
    """
    Calculates the Internal Rate of Return (IRR) for a series of uneven cash flows.
    The IRR is the discount rate that makes the Net Present Value (NPV) of all
    cash flows equal to zero.

    Args:
        cash_flows (list[float]): A list of cash flows, where the first element
                                  (index 0) is typically the initial investment (a negative value),
                                  followed by subsequent positive or negative cash flows.

    Returns:
        float: The Internal Rate of Return (as a decimal).

    Raises:
        ValueError: If the cash flows list is too short (less than 2) or if IRR
                    cannot be calculated (e.g., no sign change in cash flows,
                    or no real roots).

    Assumptions/Limitations:
    - Cash flows occur at the end of each period.
    - npf.irr uses an iterative method and may not converge for all cash flow patterns
      (e.g., multiple IRRs if cash flows change sign more than once).
    - Requires at least two cash flows, and typically at least one initial outflow followed by inflows.
    """
    if not cash_flows or len(cash_flows) < 2:
        raise ValueError("Cash flows list must contain at least two values to calculate IRR.")
    
    # npf.irr can sometimes fail or return NaN if there's no solution or multiple solutions.
    # We'll try to catch a common case for error handling.
    
    # Check for sign change, a prerequisite for a real IRR
    positive_flows = any(cf > 0 for cf in cash_flows)
    negative_flows = any(cf < 0 for cf in cash_flows)

    if not (positive_flows and negative_flows):
        raise ValueError("IRR calculation requires at least one positive and one negative cash flow to have a real solution.")

    try:
        irr = npf.irr(values=cash_flows)
        # npf.irr can return numpy.nan if no root is found.
        if np.isnan(irr):
            raise ValueError("IRR could not be calculated. No real root found or convergence failed.")
        return irr
    except Exception as e:
        # Catch more general numpy_financial errors during calculation
        raise ValueError(f"An error occurred during IRR calculation: {e}")