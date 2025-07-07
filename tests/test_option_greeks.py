#tests/test_option_greeks.py

import pytest
from mathematical_functions.option_greeks import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_theta,
    black_scholes_vega,
    black_scholes_rho,
    _d1_d2 # Helper function, good to test its error handling
)
import math

# Common parameters for testing Greeks (ATM option)
S_test = 100.0    # Stock price
K_test = 100.0    # Strike price
T_test = 0.5    # 6 months to expiration
r_test = 0.05   # Risk-free rate (5%)
sigma_test = 0.20 # Volatility (20%)
q_test = 0.0    # Dividend yield (0%)

# --- Helper function _d1_d2 error handling (shared with options_bsm) ---
# These tests are duplicated from test_options_bsm.py as _d1_d2 is used in both modules
# This duplication is acceptable for independent module testing.
def test_d1_d2_invalid_S_greeks():
    """Test _d1_d2 with non-positive S for Greeks context."""
    with pytest.raises(ValueError, match=r"Current stock price \(S\) must be positive for Greeks calculation."):
        _d1_d2(0, K_test, T_test, r_test, sigma_test, q_test)

def test_d1_d2_invalid_K_greeks():
    """Test _d1_d2 with non-positive K for Greeks context."""
    with pytest.raises(ValueError, match=r"Strike price \(K\) must be positive for Greeks calculation."):
        _d1_d2(S_test, 0, T_test, r_test, sigma_test, q_test)

def test_d1_d2_invalid_T_zero_greeks():
    """Test _d1_d2 with zero time to expiration for Greeks context."""
    with pytest.raises(ValueError, match=r"Time to expiration \(T\) must be positive for Greeks calculation."):
        _d1_d2(S_test, K_test, 0, r_test, sigma_test, q_test)

def test_d1_d2_invalid_sigma_zero_greeks():
    """Test _d1_d2 with zero volatility for Greeks context."""
    with pytest.raises(ValueError, match=r"Volatility \(sigma\) must be positive for Greeks calculation."):
        _d1_d2(S_test, K_test, T_test, r_test, 0, q_test)


# --- black_scholes_delta tests ---
def test_delta_call_atm():
    """Test Delta for an at-the-money call option (should be close to 0.5)."""
    assert black_scholes_delta(S_test, K_test, T_test, r_test, sigma_test, option_type='call') == pytest.approx(0.597734, rel=1e-5)

def test_delta_put_atm():
    """Test Delta for an at-the-the-money put option (should be close to -0.5)."""
    assert black_scholes_delta(S_test, K_test, T_test, r_test, sigma_test, option_type='put') == pytest.approx(-0.402266, rel=1e-5)

def test_delta_call_deep_itm():
    """Test Delta for a deep in-the-money call (should be close to 1)."""
    assert black_scholes_delta(120, 100, T_test, r_test, sigma_test, option_type='call') == pytest.approx(0.937816, rel=1e-5)

def test_delta_put_deep_itm():
    """Test Delta for a deep in-the-money put (should be close to -1)."""
    assert black_scholes_delta(80, 100, T_test, r_test, sigma_test, option_type='put') == pytest.approx(-0.908303, rel=1e-5)

def test_delta_call_deep_otm():
    """Test Delta for a deep out-of-the-money call (should be close to 0)."""
    assert black_scholes_delta(80, 100, T_test, r_test, sigma_test, option_type='call') == pytest.approx(0.091697, rel=1e-5)

def test_delta_put_deep_otm():
    """Test Delta for a deep out-of-the-money put (should be close to 0)."""
    assert black_scholes_delta(120, 100, T_test, r_test, sigma_test, option_type='put') == pytest.approx(-0.062184, rel=1e-5)

def test_delta_with_dividend():
    """Test Delta with a non-zero dividend yield."""
    assert black_scholes_delta(S_test, K_test, T_test, r_test, sigma_test, option_type='call', q=0.02) == pytest.approx(0.564485, rel=1e-5)
    assert black_scholes_delta(S_test, K_test, T_test, r_test, sigma_test, option_type='put', q=0.02) == pytest.approx(-0.425565, rel=1e-5)

def test_delta_invalid_option_type():
    """Test Delta with an invalid option type."""
    with pytest.raises(ValueError, match=r"option_type must be 'call' or 'put'."):
        black_scholes_delta(S_test, K_test, T_test, r_test, sigma_test, option_type='future')

# --- black_scholes_gamma tests ---
def test_gamma_atm():
    """Test Gamma for an at-the-money option (max gamma)."""
    # Corrected expected value based on calculations. Using abs tolerance for small values.
    assert black_scholes_gamma(S_test, K_test, T_test, r_test, sigma_test) == pytest.approx(0.027359, abs=1e-6)

def test_gamma_otm_itm():
    """Test Gamma for OTM/ITM options (gamma decreases as option goes deeper ITM/OTM)."""
    gamma_itm = black_scholes_gamma(120, 100, T_test, r_test, sigma_test)
    gamma_otm = black_scholes_gamma(80, 100, T_test, r_test, sigma_test)
    assert gamma_itm < black_scholes_gamma(S_test, K_test, T_test, r_test, sigma_test)
    assert gamma_otm < black_scholes_gamma(S_test, K_test, T_test, r_test, sigma_test)
    # Corrected expected values based on calculations. Using abs tolerance for small values.
    assert gamma_itm == pytest.approx(0.007218, abs=1e-6)
    assert gamma_otm == pytest.approx(0.014554, abs=1e-6)

def test_gamma_with_dividend():
    """Test Gamma with a non-zero dividend yield."""
    # Corrected expected value based on calculations. Using abs tolerance for small values.
    assert black_scholes_gamma(S_test, K_test, T_test, r_test, sigma_test, q=0.02) == pytest.approx(0.027496, abs=1e-6)

# --- black_scholes_theta tests ---
def test_theta_call_atm():
    """Test Theta for an at-the-money call option (time decay)."""
    assert black_scholes_theta(S_test, K_test, T_test, r_test, sigma_test, option_type='call') == pytest.approx(-8.115967, rel=1e-5)

def test_theta_put_atm():
    """Test Theta for an at-the-money put option (time decay)."""
    assert black_scholes_theta(S_test, K_test, T_test, r_test, sigma_test, option_type='put') == pytest.approx(-3.239418, rel=1e-5)

def test_theta_with_dividend():
    """Test Theta with a non-zero dividend yield."""
    # CORRECTED EXPECTED VALUE based on manual calculation.
    assert black_scholes_theta(S_test, K_test, T_test, r_test, sigma_test, option_type='call', q=0.02) == pytest.approx(-6.877232, rel=1e-5)
    # CORRECTED EXPECTED VALUE based on manual calculation.
    assert black_scholes_theta(S_test, K_test, T_test, r_test, sigma_test, option_type='put', q=0.02) == pytest.approx(-3.980782, rel=1e-5)


# --- black_scholes_vega tests ---
def test_vega_atm():
    """Test Vega for an at-the-money option (max vega)."""
    assert black_scholes_vega(S_test, K_test, T_test, r_test, sigma_test) == pytest.approx(27.358659, rel=1e-5)

def test_vega_otm_itm():
    """Test Vega for OTM/ITM options (vega decreases as option goes deeper ITM/OTM)."""
    vega_itm = black_scholes_vega(120, 100, T_test, r_test, sigma_test)
    vega_otm = black_scholes_vega(80, 100, T_test, r_test, sigma_test)
    assert vega_itm < black_scholes_vega(S_test, K_test, T_test, r_test, sigma_test)
    assert vega_otm < black_scholes_vega(S_test, K_test, T_test, r_test, sigma_test)
    assert vega_itm == pytest.approx(10.394358, rel=1e-5)
    assert vega_otm == pytest.approx(9.314428, rel=1e-5)

def test_vega_with_dividend():
    """Test Vega with a non-zero dividend yield."""
    assert black_scholes_vega(S_test, K_test, T_test, r_test, sigma_test, q=0.02) == pytest.approx(27.495794, rel=1e-5)

# --- black_scholes_rho tests ---
def test_rho_call_atm():
    """Test Rho for an at-the-money call option."""
    assert black_scholes_rho(S_test, K_test, T_test, r_test, sigma_test, option_type='call') == pytest.approx(26.442359, rel=1e-5)

def test_rho_put_atm():
    """Test Rho for an at-the-money put option."""
    assert black_scholes_rho(S_test, K_test, T_test, r_test, sigma_test, option_type='put') == pytest.approx(-22.323136, rel=1e-5)

def test_rho_with_dividend():
    """Test Rho with a non-zero dividend yield."""
    assert black_scholes_rho(S_test, K_test, T_test, r_test, sigma_test, option_type='call', q=0.02) == pytest.approx(25.070429, rel=1e-5)
    assert black_scholes_rho(S_test, K_test, T_test, r_test, sigma_test, option_type='put', q=0.02) == pytest.approx(-23.695066, rel=1e-5)