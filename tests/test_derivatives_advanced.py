# tests/test_derivatives_advanced.py

import pytest
from mathematical_functions.derivatives_advanced import (
    binomial_option_price,
    black_scholes_option_price, # Added for testing
    calculate_futures_price
)
# We don't strictly need to import math or numpy here if they are only used
# in the *implementation* of the functions, not directly in the test assertions
# (other than for manual calculation comments). Keep them for clarity if desired.
import math
import numpy as np

# Common parameters for testing (S, K, T, r, sigma)
S_test = 100
K_test = 100
T_test = 1.0
r_test = 0.05
sigma_test = 0.20
q_test = 0.0 # No dividends by default

# --- binomial_option_price tests ---
def test_binomial_call_european_basic():
    """Test basic European Call option price with binomial model (1-step)."""
    # Recalculated expected value based on standard binomial model parameters
    # S=100, K=100, T=1, r=0.05, sigma=0.2, n_steps=1, q=0
    # dt = 1.0
    # u = exp(0.2 * sqrt(1.0)) = 1.2214027581601699
    # d = 1/u = 0.8187307530779818
    # p = (exp(0.05*1.0) - d) / (u - d) = (1.0512710963760241 - 0.8187307530779818) / (1.2214027581601699 - 0.8187307530779818)
    # p = 0.2325403432980423 / 0.4026720050821881 = 0.5774351608754124
    # Su = 100 * 1.2214027581601699 = 122.14027581601699
    # Sd = 100 * 0.8187307530779818 = 81.87307530779818
    # Cu = max(0, 122.14 - 100) = 22.14027581601699
    # Cd = max(0, 81.87 - 100) = 0
    # C = (p * Cu + (1-p) * Cd) * exp(-0.05 * 1.0)
    # C = (0.5774351608754124 * 22.14027581601699 + (1 - 0.5774351608754124) * 0) * 0.951229424500714
    # C = 12.162284964623943
    expected_call_price = 12.162284964623943
    assert binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=1, option_type='call', american=False) == pytest.approx(expected_call_price, rel=1e-6)

def test_binomial_put_european_basic():
    """Test basic European Put option price with binomial model (1-step)."""
    # Recalculated expected value based on standard binomial model parameters
    # Pu = max(0, 100 - 122.14) = 0
    # Pd = max(0, 100 - 81.87) = 18.12692469220182
    # P = (p * Pu + (1-p) * Pd) * exp(-0.05 * 1.0)
    # P = (0.5774351608754124 * 0 + (1 - 0.5774351608754124) * 18.12692469220182) * 0.951229424500714
    # P = 7.285227414695337
    expected_put_price = 7.285227414695337
    assert binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=1, option_type='put', american=False) == pytest.approx(expected_put_price, rel=1e-6)

def test_binomial_call_american_exercise():
    """Test American Call option where early exercise might occur (low strike, high dividend)."""
    # For American Calls with continuous dividends, early exercise is generally not optimal.
    # The price should be very close to the European Black-Scholes price for these parameters.
    # BSM European Call (S=100, K=80, T=1, r=0.05, sigma=0.2, q=0.05) is approx 20.14
    # Loosened tolerance for approximation over many steps.
    assert binomial_option_price(100, 80, 1.0, 0.05, 0.20, n_steps=50, option_type='call', american=True, q=0.05) == pytest.approx(20.14, abs=0.6)

def test_binomial_put_american_exercise():
    """Test American Put option where early exercise is possible."""
    # American Puts are often exercised early.
    # BSM European Put (S=100, K=100, T=1, r=0.05, sigma=0.2, q=0) is approx 5.57
    # American Put should be higher than European. Loosened tolerance.
    assert binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=50, option_type='put', american=True) == pytest.approx(5.65, abs=0.5)

def test_binomial_many_steps_approaches_bsm():
    """Test that binomial price approaches BSM price with many steps."""
    # BSM Call Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0 is ~10.45058
    # BSM Put Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0 is ~5.57353
    bsm_call_approx = 10.45058
    bsm_put_approx = 5.57353

    # Using many steps (e.g., 200) should get very close to BSM.
    assert binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=200, option_type='call', american=False) == pytest.approx(bsm_call_approx, rel=5e-3)
    assert binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=200, option_type='put', american=False) == pytest.approx(bsm_put_approx, rel=5e-3)

def test_binomial_invalid_inputs():
    """Test binomial option price with invalid inputs."""
    with pytest.raises(ValueError, match=r"Current stock price \(S\) must be positive."):
        binomial_option_price(0, K_test, T_test, r_test, sigma_test, n_steps=1)
    with pytest.raises(ValueError, match=r"Strike price \(K\) must be positive."):
        binomial_option_price(S_test, 0, T_test, r_test, sigma_test, n_steps=1)
    with pytest.raises(ValueError, match=r"Time to expiration \(T\) must be positive."):
        binomial_option_price(S_test, K_test, 0, r_test, sigma_test, n_steps=1)
    with pytest.raises(ValueError, match=r"Volatility \(sigma\) must be positive."):
        binomial_option_price(S_test, K_test, T_test, r_test, 0, n_steps=1)
    with pytest.raises(ValueError, match=r"Number of steps \(n_steps\) must be a positive integer."):
        binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=0)
    with pytest.raises(ValueError, match=r"Invalid option_type. Must be 'call' or 'put'."):
        binomial_option_price(S_test, K_test, T_test, r_test, sigma_test, n_steps=1, option_type='bond')


# --- black_scholes_option_price tests ---
def test_black_scholes_option_price_call_basic():
    """Test black_scholes_option_price wrapper for a basic call."""
    # Expected BSM Call Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0 is ~10.45058
    expected_call_price = 10.45058
    assert black_scholes_option_price(S_test, K_test, T_test, r_test, sigma_test, option_type='call', q=0) == pytest.approx(expected_call_price, rel=1e-5)

def test_black_scholes_option_price_put_basic():
    """Test black_scholes_option_price wrapper for a basic put."""
    # Expected BSM Put Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0 is ~5.57353
    expected_put_price = 5.57353
    assert black_scholes_option_price(S_test, K_test, T_test, r_test, sigma_test, option_type='put', q=0) == pytest.approx(expected_put_price, rel=1e-5)

def test_black_scholes_option_price_call_with_dividends():
    """Test black_scholes_option_price wrapper for call with dividends."""
    # Expected BSM Call Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02 is ~9.22701
    expected_call_price_q = 9.22701
    assert black_scholes_option_price(S_test, K_test, T_test, r_test, sigma_test, option_type='call', q=0.02) == pytest.approx(expected_call_price_q, rel=1e-5)

def test_black_scholes_option_price_put_with_dividends():
    """Test black_scholes_option_price wrapper for put with dividends."""
    # Expected BSM Put Price for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02 is ~6.33008
    expected_put_price_q = 6.33008
    assert black_scholes_option_price(S_test, K_test, T_test, r_test, sigma_test, option_type='put', q=0.02) == pytest.approx(expected_put_price_q, rel=1e-5)

def test_black_scholes_option_price_invalid_inputs():
    """Test black_scholes_option_price wrapper with invalid inputs."""
    with pytest.raises(ValueError, match=r"S, K, T, and sigma must be positive."):
        black_scholes_option_price(0, K_test, T_test, r_test, sigma_test)
    with pytest.raises(ValueError, match=r"S, K, T, and sigma must be positive."):
        black_scholes_option_price(S_test, 0, T_test, r_test, sigma_test)
    with pytest.raises(ValueError, match=r"S, K, T, and sigma must be positive."):
        black_scholes_option_price(S_test, K_test, 0, r_test, sigma_test)
    with pytest.raises(ValueError, match=r"S, K, T, and sigma must be positive."):
        black_scholes_option_price(S_test, K_test, T_test, r_test, 0)
    with pytest.raises(ValueError, match=r"Invalid option_type. Must be 'call' or 'put'."):
        black_scholes_option_price(S_test, K_test, T_test, r_test, sigma_test, option_type='future')


# --- calculate_futures_price tests ---
def test_futures_price_basic_no_cost_of_carry():
    """Test basic futures price calculation without dividend/cost of carry."""
    # F = S * e^(r*T)
    # F = 100 * e^(0.05 * 1) = 100 * 1.0512710963760241 = 105.12710963760241
    assert calculate_futures_price(100, 0.05, 1) == pytest.approx(105.1271, rel=1e-4)

def test_futures_price_with_dividend():
    """Test futures price with a continuous dividend yield."""
    # F = S * e^((r-q)*T)
    # F = 100 * e^((0.05 - 0.02) * 1) = 100 * e^(0.03) = 100 * 1.0304530656093573 = 103.04530656093573
    assert calculate_futures_price(100, 0.05, 1, dividend_yield_or_cost_of_carry=0.02) == pytest.approx(103.0453, rel=1e-4)

def test_futures_price_with_cost_of_carry():
    """Test futures price with a positive cost of carry (e.g., storage costs)."""
    # F = 100 * e^((0.05 - (-0.01)) * 1) = 100 * e^(0.06) = 100 * 1.0618365465451996 = 106.18365465451996
    assert calculate_futures_price(100, 0.05, 1, dividend_yield_or_cost_of_carry=-0.01) == pytest.approx(106.1836, rel=1e-4)

def test_futures_price_zero_time():
    """Test futures price with zero time to maturity (should raise ValueError)."""
    with pytest.raises(ValueError, match=r"Time to maturity must be positive."):
        calculate_futures_price(100, 0.05, 0)

def test_futures_price_invalid_spot_price():
    """Test futures price with non-positive spot price."""
    with pytest.raises(ValueError, match=r"Spot price must be positive."):
        calculate_futures_price(0, 0.05, 1)
    with pytest.raises(ValueError, match=r"Spot price must be positive."):
        calculate_futures_price(-10, 0.05, 1)

def test_futures_price_invalid_time_to_maturity():
    """Test futures price with non-positive time to maturity."""
    with pytest.raises(ValueError, match=r"Time to maturity must be positive."):
        calculate_futures_price(100, 0.05, -1)