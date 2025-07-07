# tests/test_capital_budgeting.py

import pytest
import math
import numpy_financial as npf # Required for verifying NPV/IRR in some tests
# Update this import to refer to the module within the package
from mathematical_functions.capital_budgeting import (
    calculate_payback_period,
    calculate_discounted_payback_period,
    calculate_npv,
    calculate_irr,
    calculate_profitability_index
)

# Using pytest, we define test functions directly instead of classes/methods
# Test functions must start with 'test_'

# --- Tests for calculate_payback_period ---

def test_payback_period_exact_recovery():
    # Investment recovered exactly at the end of a period
    initial_investment = -10000
    cash_flows = [2000, 3000, 5000]
    expected_payback = 3.0
    assert math.isclose(calculate_payback_period(initial_investment, cash_flows), expected_payback)

def test_payback_period_fractional_recovery():
    # Investment recovered within a period
    initial_investment = -10000
    cash_flows = [3000, 4000, 6000]
    expected_payback = 2.5 # 3000 + 4000 = 7000. Need 3000 more. 3000 / 6000 = 0.5. So 2 + 0.5 = 2.5
    assert math.isclose(calculate_payback_period(initial_investment, cash_flows), expected_payback)

def test_payback_period_never_recovered():
    # Cash flows not sufficient to recover initial investment
    initial_investment = -20000
    cash_flows = [3000, 4000, 5000]
    assert calculate_payback_period(initial_investment, cash_flows) == float('inf')

def test_payback_period_empty_cash_flows():
    # Test case for empty cash flows
    with pytest.raises(ValueError, match=r"Cash flows list cannot be empty."):
        calculate_payback_period(initial_investment=-1000, cash_flows=[])

def test_payback_period_non_negative_initial_investment_error():
    # Test case for initial_investment >= 0
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_payback_period(initial_investment=10000, cash_flows=[3000, 4000, 5000])
    
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_payback_period(initial_investment=0, cash_flows=[3000, 4000, 5000])

def test_payback_period_non_positive_cash_flow_error():
    # Test case for non-positive cash flows
    with pytest.raises(ValueError, match=r"All cash flows \(inflows\) must be positive."):
        calculate_payback_period(initial_investment=-10000, cash_flows=[3000, -2000, 5000])

    with pytest.raises(ValueError, match=r"All cash flows \(inflows\) must be positive."):
        calculate_payback_period(initial_investment=-10000, cash_flows=[3000, 0, 5000])

def test_payback_period_large_numbers():
    # Test with larger numbers
    initial_investment = -1_000_000
    cash_flows = [200_000, 300_000, 400_000, 500_000]
    expected_payback = 3.2 # 200+300+400 = 900k. Need 100k. 100k/500k = 0.2. So 3 + 0.2 = 3.2
    assert math.isclose(calculate_payback_period(initial_investment, cash_flows), expected_payback)

# --- Tests for calculate_discounted_payback_period ---

def test_discounted_payback_period_exact_recovery():
    # Investment recovered exactly at the end of a period
    initial_investment = -10000
    cash_flows = [4000, 5000, 3000]
    discount_rate = 0.10
    # Manual calculation for expected value
    dcf1 = cash_flows[0] / (1 + discount_rate)**1
    dcf2 = cash_flows[1] / (1 + discount_rate)**2
    dcf3 = cash_flows[2] / (1 + discount_rate)**3
    
    cumulative_dcf_period2 = dcf1 + dcf2
    amount_needed_from_period3 = abs(initial_investment) - cumulative_dcf_period2
    expected_payback = 2 + (amount_needed_from_period3 / dcf3)
    
    assert math.isclose(calculate_discounted_payback_period(
        initial_investment, cash_flows, discount_rate
    ), expected_payback, rel_tol=1e-6) # Use rel_tol for float comparisons

def test_discounted_payback_period_fractional_recovery():
    # Investment recovered within a period
    initial_investment = -10000
    cash_flows = [5000, 6000, 7000]
    discount_rate = 0.05
    
    # Manual calculation to derive expected value
    dcf1 = 5000 / (1 + 0.05)**1 # 4761.90476
    dcf2 = 6000 / (1 + 0.05)**2 # 5442.17687
    
    # After Year 1, remaining = 10000 - 4761.90476 = 5238.09524
    # This amount is recovered in Year 2.
    # Fraction of Year 2 needed: 5238.09524 / 5442.17687 = 0.962499
    expected_payback = 1 + (abs(initial_investment) - dcf1) / dcf2
    
    assert math.isclose(calculate_discounted_payback_period(
        initial_investment, cash_flows, discount_rate
    ), expected_payback, rel_tol=1e-6)

def test_discounted_payback_period_never_recovered():
    # Discounted cash flows not sufficient
    initial_investment = -100000
    cash_flows = [10000, 20000, 30000]
    discount_rate = 0.15
    assert calculate_discounted_payback_period(
        initial_investment, cash_flows, discount_rate
    ) == float('inf')

def test_discounted_payback_period_zero_discount_rate():
    # Should behave like normal payback period if discount rate is 0
    initial_investment = -10000
    cash_flows = [3000, 4000, 6000]
    discount_rate = 0.0
    expected_payback = 2.5
    assert math.isclose(calculate_discounted_payback_period(
        initial_investment, cash_flows, discount_rate
    ), expected_payback)

def test_discounted_payback_period_high_discount_rate():
    # Very high discount rate might make recovery take longer or never happen
    initial_investment = -1000
    cash_flows = [600, 600]
    discount_rate = 0.50 # High rate
    # DCF1 = 600 / 1.5 = 400
    # DCF2 = 600 / (1.5)^2 = 266.666...
    # Total DCF = 400 + 266.666... = 666.666... (less than 1000)
    assert calculate_discounted_payback_period(
        initial_investment, cash_flows, discount_rate
    ) == float('inf')

def test_discounted_payback_period_empty_cash_flows():
    # Test case for empty cash flows
    with pytest.raises(ValueError, match=r"Cash flows list cannot be empty."):
        calculate_discounted_payback_period(initial_investment=-1000, cash_flows=[], discount_rate=0.1)

def test_discounted_payback_period_non_negative_initial_investment_error():
    # Test case for initial_investment >= 0
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_discounted_payback_period(initial_investment=10000, cash_flows=[3000, 4000, 5000], discount_rate=0.1)
    
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_discounted_payback_period(initial_investment=0, cash_flows=[3000, 4000, 5000], discount_rate=0.1)

def test_discounted_payback_period_non_positive_cash_flow_error():
    # Test case for non-positive cash flows
    with pytest.raises(ValueError, match=r"All cash flows \(inflows\) must be positive."):
        calculate_discounted_payback_period(initial_investment=-10000, cash_flows=[3000, -2000, 5000], discount_rate=0.1)

    with pytest.raises(ValueError, match=r"All cash flows \(inflows\) must be positive."):
        calculate_discounted_payback_period(initial_investment=-10000, cash_flows=[3000, 0, 5000], discount_rate=0.1)

def test_discounted_payback_period_negative_discount_rate_error():
    # Test case for negative discount rate
    with pytest.raises(ValueError, match=r"Discount rate cannot be negative."):
        calculate_discounted_payback_period(initial_investment=-10000, cash_flows=[3000, 4000, 5000], discount_rate=-0.05)


# --- Tests for calculate_npv ---

def test_npv_positive():
    # A standard case resulting in a positive NPV
    rate = 0.10
    cash_flows = [-10000, 3000, 4000, 5000, 3000]
    expected_npv = npf.npv(rate, cash_flows) # Use numpy_financial for verification
    assert math.isclose(calculate_npv(rate, cash_flows), expected_npv)

def test_npv_negative():
    # A standard case resulting in a negative NPV
    rate = 0.12
    cash_flows = [-10000, 2000, 3000, 2000, 1000]
    expected_npv = npf.npv(rate, cash_flows)
    assert math.isclose(calculate_npv(rate, cash_flows), expected_npv)

def test_npv_zero():
    # Cash flows that result in an NPV close to zero at a specific rate
    cash_flows_for_zero_npv = [-1000, 300, 300, 300, 300]
    rate_for_zero_npv = npf.irr(cash_flows_for_zero_npv) # IRR makes NPV zero
    assert math.isclose(calculate_npv(rate_for_zero_npv, cash_flows_for_zero_npv), 0.0, abs_tol=1e-9)

def test_npv_zero_rate():
    # When discount rate is zero, NPV is just the sum of cash flows
    rate = 0.0
    cash_flows = [-10000, 3000, 4000, 5000]
    expected_npv = sum(cash_flows)
    assert math.isclose(calculate_npv(rate, cash_flows), expected_npv)

def test_npv_only_initial_investment():
    # If only initial investment is provided, NPV is just that amount
    rate = 0.10
    cash_flows = [-5000]
    expected_npv = -5000.0 # No future cash flows to discount
    assert math.isclose(calculate_npv(rate, cash_flows), expected_npv)

def test_npv_empty_cash_flows():
    # Test case for empty cash flows list
    with pytest.raises(ValueError, match=r"Cash flows list cannot be empty."):
        calculate_npv(rate=0.10, cash_flows=[])

def test_npv_rate_less_than_neg_one_error():
    # Test case for discount rate less than -1 (-100%)
    with pytest.raises(ValueError, match=r"The discount rate \(rate\) must be greater than -1 \(or -100%\)."):
        calculate_npv(rate=-1.1, cash_flows=[-100, 50, 60])

def test_npv_rate_equals_neg_one_error():
    # Test case for discount rate equal to -1 (-100%)
    with pytest.raises(ValueError, match=r"The discount rate \(rate\) must be greater than -1 \(or -100%\)."):
        calculate_npv(rate=-1.0, cash_flows=[-100, 50, 60])

def test_npv_with_mixed_future_cash_flows():
    # Test with both positive and negative future cash flows
    rate = 0.05
    cash_flows = [-5000, 2000, -500, 3000, 1000]
    expected_npv = npf.npv(rate, cash_flows)
    assert math.isclose(calculate_npv(rate, cash_flows), expected_npv)


# --- Tests for calculate_irr ---

def test_irr_standard_case():
    # A typical project with a clear IRR
    cash_flows = [-10000, 3000, 4000, 5000, 3000]
    expected_irr = npf.irr(cash_flows)
    assert math.isclose(calculate_irr(cash_flows), expected_irr)

def test_irr_simple_case():
    # Simpler case for direct calculation verification
    # If initial_investment = -100 and first_year_return = 120
    # IRR = (120 - 100) / 100 = 0.20 or 20%
    cash_flows = [-100, 120]
    expected_irr = 0.20
    assert math.isclose(calculate_irr(cash_flows), expected_irr)

def test_irr_negative_irr():
    # Project with a negative IRR
    cash_flows = [-1000, 100, 100, 100, 100] # Inflows much smaller than initial investment
    expected_irr = npf.irr(cash_flows)
    assert math.isclose(calculate_irr(cash_flows), expected_irr)

def test_irr_empty_cash_flows():
    # Test case for empty cash flows list
    with pytest.raises(ValueError, match=r"Cash flows list cannot be empty."):
        calculate_irr(cash_flows=[])

def test_irr_no_sign_change_all_positive():
    # All cash flows are positive (no initial outflow or negative cash flow)
    with pytest.raises(ValueError, match=r"Cash flows must contain at least one positive and one negative value for IRR calculation."):
        calculate_irr(cash_flows=[100, 200, 300])

def test_irr_no_sign_change_all_negative():
    # All cash flows are negative (or zero after initial)
    with pytest.raises(ValueError, match=r"Cash flows must contain at least one positive and one negative value for IRR calculation."):
        calculate_irr(cash_flows=[-100, -50, -20])

def test_irr_no_sign_change_only_initial_negative():
    # Only initial investment is negative, subsequent are zero
    with pytest.raises(ValueError, match=r"Cash flows must contain at least one positive and one negative value for IRR calculation."):
        calculate_irr(cash_flows=[-1000, 0, 0, 0])

def test_irr_complex_cash_flows():
    # Test with complex cash flows that might have multiple IRRs (though npf.irr returns one)
    # The important thing is that it runs without error and gives the same as numpy_financial
    cash_flows = [-1000, 400, 400, 400, -200] # Sign changes twice
    expected_irr = npf.irr(cash_flows)
    assert math.isclose(calculate_irr(cash_flows), expected_irr)

# --- Tests for calculate_profitability_index ---

def test_profitability_index_greater_than_one():
    # PI > 1, acceptable project
    initial_investment = -10000
    future_cash_flows = [3000, 4000, 5000, 3000]
    discount_rate = 0.10
    
    # PV of future cash flows using npf.npv (first element 0)
    pv_future_cf = npf.npv(discount_rate, [0] + future_cash_flows)
    expected_pi = pv_future_cf / abs(initial_investment)
    
    assert math.isclose(calculate_profitability_index(
        initial_investment, future_cash_flows, discount_rate
    ), expected_pi, rel_tol=1e-9)

def test_profitability_index_less_than_one():
    # PI < 1, unacceptable project
    initial_investment = -10000
    future_cash_flows = [1000, 2000, 3000]
    discount_rate = 0.10
    
    pv_future_cf = npf.npv(discount_rate, [0] + future_cash_flows)
    expected_pi = pv_future_cf / abs(initial_investment)
    
    assert math.isclose(calculate_profitability_index(
        initial_investment, future_cash_flows, discount_rate
    ), expected_pi, rel_tol=1e-9)

def test_profitability_index_equal_to_one():
    # PI = 1, breaks even on a PV basis
    initial_investment = -10000
    # Manually calculate future cash flows that give a PV of 10000
    # For example, PV of 11000 at 10% for 1 year is 10000
    future_cash_flows = [11000]
    discount_rate = 0.10
    
    pv_future_cf = npf.npv(discount_rate, [0] + future_cash_flows)
    expected_pi = pv_future_cf / abs(initial_investment)
    
    assert math.isclose(calculate_profitability_index(
        initial_investment, future_cash_flows, discount_rate
    ), expected_pi, rel_tol=1e-9)

def test_profitability_index_zero_discount_rate():
    # PI with zero discount rate
    initial_investment = -10000
    future_cash_flows = [3000, 4000, 5000]
    discount_rate = 0.0
    
    # PV of future cash flows is just the sum
    pv_future_cf = sum(future_cash_flows)
    expected_pi = pv_future_cf / abs(initial_investment)
    
    assert math.isclose(calculate_profitability_index(
        initial_investment, future_cash_flows, discount_rate
    ), expected_pi)

def test_profitability_index_empty_future_cash_flows():
    # Test case for empty future cash flows list
    with pytest.raises(ValueError, match=r"Future cash flows list cannot be empty."):
        calculate_profitability_index(initial_investment=-1000, cash_flows=[], discount_rate=0.1)

def test_profitability_index_non_negative_initial_investment_error():
    # Test case for initial_investment >= 0
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_profitability_index(initial_investment=10000, cash_flows=[3000, 4000, 5000], discount_rate=0.1)

# Corrected test for initial_investment = 0.
# It should now expect the general "initial investment must be a negative value" error.
def test_profitability_index_zero_initial_investment_error():
    # Test case for initial_investment = 0
    # This falls under the initial 'initial_investment >= 0' check.
    with pytest.raises(ValueError, match=r"Initial investment must be a negative value representing an outflow."):
        calculate_profitability_index(initial_investment=0, cash_flows=[3000, 4000, 5000], discount_rate=0.1)


def test_profitability_index_rate_less_than_neg_one_error():
    # Test case for discount rate less than -1 (-100%)
    with pytest.raises(ValueError, match=r"The discount rate \(rate\) must be greater than -1 \(or -100%\)."):
        calculate_profitability_index(initial_investment=-1000, cash_flows=[500, 600], discount_rate=-1.1)

def test_profitability_index_rate_equals_neg_one_error():
    # Test case for discount rate equal to -1 (-100%)
    with pytest.raises(ValueError, match=r"The discount rate \(rate\) must be greater than -1 \(or -100%\)."):
        calculate_profitability_index(initial_investment=-1000, cash_flows=[500, 600], discount_rate=-1.0)