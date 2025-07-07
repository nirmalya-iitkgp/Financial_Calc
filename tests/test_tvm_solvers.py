# tests/test_tvm_solvers.py

import pytest
import numpy as np
from mathematical_functions.tvm_solvers import (
    calculate_npv,
    calculate_irr
)

# --- calculate_npv tests ---
def test_npv_basic():
    """Test NPV calculation with a simple set of cash flows."""
    cash_flows = [-100, 20, 30, 40, 50]
    rate = 0.10
    # NPV = -100 + 20/(1.10)^1 + 30/(1.10)^2 + 40/(1.10)^3 + 50/(1.10)^4
    # NPV = -100 + 18.1818 + 24.7934 + 30.0526 + 34.1507 = 7.1785
    assert calculate_npv(rate, cash_flows) == pytest.approx(7.1785, rel=1e-4)

def test_npv_positive_initial_investment():
    """
    Test NPV with a positive initial cash flow (e.g., immediate revenue).
    The numpy_financial.npv function treats the first value as time 0.
    """
    cash_flows = [100, 20, 30, 40, 50] # Initial inflow
    rate = 0.10
    # Calculation: 100 + 20/(1.10)^1 + 30/(1.10)^2 + 40/(1.10)^3 + 50/(1.10)^4
    # This is 100 (initial inflow) + 7.1785 (NPV of subsequent flows) = 207.1785
    assert calculate_npv(rate, cash_flows) == pytest.approx(207.1785, rel=1e-4)

def test_npv_zero_rate():
    """Test NPV with a zero discount rate (should be sum of cash flows)."""
    cash_flows = [-100, 20, 30, 40, 50]
    rate = 0.0
    assert calculate_npv(rate, cash_flows) == pytest.approx(sum(cash_flows))

def test_npv_only_initial_investment():
    """Test NPV with only an initial investment (no future cash flows)."""
    cash_flows = [-1000]
    rate = 0.05
    assert calculate_npv(rate, cash_flows) == pytest.approx(-1000.0)

def test_npv_all_negative_cash_flows():
    """Test NPV with all negative cash flows."""
    cash_flows = [-100, -20, -30]
    rate = 0.05
    # NPV = -100 - 20/(1.05) - 30/(1.05)^2 = -100 - 19.0476 - 27.2109 = -146.2585
    assert calculate_npv(rate, cash_flows) == pytest.approx(-146.2585, rel=1e-4)

def test_npv_invalid_empty_cash_flows():
    """Test NPV with an empty cash flows list."""
    with pytest.raises(ValueError, match="Cash flows list cannot be empty."):
        calculate_npv(0.05, [])

def test_npv_invalid_rate_below_neg_one():
    """Test NPV with an invalid (below -1) rate."""
    with pytest.raises(ValueError, match="Rate cannot be less than -1"):
        calculate_npv(-1.1, [-100, 50, 60])

# --- calculate_irr tests ---
def test_irr_basic():
    """Test IRR calculation with a simple set of cash flows."""
    cash_flows = [-100, 20, 30, 40, 50]
    # Corrected Expected IRR for these cash flows is approximately 0.128257 or 12.83%
    assert calculate_irr(cash_flows) == pytest.approx(0.128257, rel=1e-4)

def test_irr_simple_project():
    """Test IRR for a typical project with initial outflow and subsequent inflows."""
    cash_flows = [-100000, 20000, 30000, 40000, 50000, 60000]
    # Corrected Expected IRR for these cash flows is approximately 0.232919 or 23.29%
    assert calculate_irr(cash_flows) == pytest.approx(0.232919, rel=1e-4)

def test_irr_multiple_sign_changes_might_fail():
    """
    Test IRR with multiple sign changes (which can lead to multiple IRRs or no real solution).
    Numpy_financial's IRR might return NaN or raise an error for such cases.
    We are expecting a ValueError if it cannot find a real root.
    """
    # Example that might have multiple IRRs (e.g., 0% and 100% for [-100, 200, -100])
    # npf.irr typically returns one of the real roots if multiple exist, or NaN if none converge.
    cash_flows_multiple_irr = [-100, 200, -100]
    irr_val = calculate_irr(cash_flows_multiple_irr)
    assert isinstance(irr_val, float)
    # Ensure NPV is close to zero at this calculated rate
    assert calculate_npv(irr_val, cash_flows_multiple_irr) == pytest.approx(0.0, abs=1e-6)

    # Test case for no sign change (all negative after initial or all positive)
    # This should raise a ValueError due to the explicit check in calculate_irr.
    cash_flows_no_sign_change = [-100, -50, -20]
    with pytest.raises(ValueError, match="IRR calculation requires at least one positive and one negative cash flow"):
        calculate_irr(cash_flows_no_sign_change)

    cash_flows_only_inflows = [100, 50, 20]
    with pytest.raises(ValueError, match="IRR calculation requires at least one positive and one negative cash flow"):
        calculate_irr(cash_flows_only_inflows)

def test_irr_empty_cash_flows():
    """Test IRR with an empty cash flows list."""
    with pytest.raises(ValueError, match="Cash flows list must contain at least two values to calculate IRR."):
        calculate_irr([])

def test_irr_single_cash_flow():
    """Test IRR with a single cash flow."""
    with pytest.raises(ValueError, match="Cash flows list must contain at least two values to calculate IRR."):
        calculate_irr([-100])

# Removed test_irr_no_real_solution_scenario as it was expecting a ValueError
# for a case where numpy_financial.irr actually finds a valid (negative) IRR.
# The error handling for np.isnan is covered, and the sign-change checks
# in calculate_irr already handle cases where no real root is expected due to
# lack of sign changes.