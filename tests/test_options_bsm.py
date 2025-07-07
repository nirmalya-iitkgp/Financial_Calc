# tests/test_options_bsm.py

import pytest
from mathematical_functions.options_bsm import (
    black_scholes_call_price,
    black_scholes_put_price,
    _d1_d2 # Testing helper is good practice for complex internal logic
)
import math
from scipy.stats import norm # Import norm to verify d1/d2 and cdf calls

# Common parameters for testing
S_test = 100    # Stock price
K_test = 100    # Strike price
T_test = 1.0    # 1 year to expiration
r_test = 0.05   # Risk-free rate (5%)
sigma_test = 0.20 # Volatility (20%)
q_test = 0.02   # Dividend yield (2%)

# --- _d1_d2 helper function tests ---
def test_d1_d2_basic():
    """Test d1 and d2 calculation with basic parameters."""
    d1, d2 = _d1_d2(S_test, K_test, T_test, r_test, sigma_test, q=0)
    # Re-calculate d1, d2 for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0
    # d1 = (ln(100/100) + (0.05 - 0 + 0.5 * 0.2^2) * 1) / (0.2 * sqrt(1))
    # d1 = (0 + (0.05 + 0.02) * 1) / 0.2 = 0.07 / 0.2 = 0.35
    # d2 = 0.35 - 0.2 = 0.15
    assert d1 == pytest.approx(0.35)
    assert d2 == pytest.approx(0.15)

def test_d1_d2_with_dividend():
    """Test d1 and d2 calculation with dividend yield."""
    d1, d2 = _d1_d2(S_test, K_test, T_test, r_test, sigma_test, q_test)
    # Re-calculate d1, d2 for S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02
    # d1 = (ln(100/100) + (0.05 - 0.02 + 0.5 * 0.2^2) * 1) / (0.2 * sqrt(1))
    # d1 = (0 + (0.03 + 0.02) * 1) / 0.2 = 0.05 / 0.2 = 0.25
    # d2 = 0.25 - 0.2 = 0.05
    assert d1 == pytest.approx(0.25)
    assert d2 == pytest.approx(0.05)

def test_d1_d2_invalid_S():
    """Test _d1_d2 with non-positive S."""
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive for d1/d2 calculation."):
        _d1_d2(0, K_test, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive for d1/d2 calculation."):
        _d1_d2(-10, K_test, T_test, r_test, sigma_test, q_test)

def test_d1_d2_invalid_K():
    """Test _d1_d2 with non-positive K."""
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive for d1/d2 calculation."):
        _d1_d2(S_test, 0, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive for d1/d2 calculation."):
        _d1_d2(S_test, -10, T_test, r_test, sigma_test, q_test)

def test_d1_d2_invalid_T_zero():
    """Test d1_d2 with zero time to expiration."""
    with pytest.raises(ValueError, match="Time to expiration \(T\) must be positive."):
        _d1_d2(S_test, K_test, 0, r_test, sigma_test, q_test)

def test_d1_d2_invalid_T_negative():
    """Test d1_d2 with negative time to expiration."""
    with pytest.raises(ValueError, match="Time to expiration \(T\) must be positive."):
        _d1_d2(S_test, K_test, -0.5, r_test, sigma_test, q_test)

def test_d1_d2_invalid_sigma_zero():
    """Test d1_d2 with zero volatility."""
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        _d1_d2(S_test, K_test, T_test, r_test, 0, q_test)

def test_d1_d2_invalid_sigma_negative():
    """Test d1_d2 with negative volatility."""
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        _d1_d2(S_test, K_test, T_test, r_test, -0.1, q_test)

# --- black_scholes_call_price tests ---
def test_bsm_call_price_itm():
    """Test in-the-money call option price."""
    # S=110, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from code output: 17.66295374059044
    assert black_scholes_call_price(110, 100, 1.0, 0.05, 0.20) == pytest.approx(17.663, rel=1e-3)

def test_bsm_call_price_atm():
    """Test at-the-money call option price."""
    # S=100, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from previous checks: 10.450
    assert black_scholes_call_price(100, 100, 1.0, 0.05, 0.20) == pytest.approx(10.450, rel=1e-3)

def test_bsm_call_price_otm():
    """Test out-of-the-money call option price."""
    # S=90, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from code output: 5.091222078817552
    assert black_scholes_call_price(90, 100, 1.0, 0.05, 0.20) == pytest.approx(5.091, rel=1e-3)

def test_bsm_call_price_zero_time_to_expiration():
    """Test call price with zero time to expiration (should be max(0, S-K))."""
    # For very short T, the price should approach intrinsic value
    assert black_scholes_call_price(105, 100, 0.0001, 0.05, 0.20) == pytest.approx(5.0, abs=1e-2)
    assert black_scholes_call_price(95, 100, 0.0001, 0.05, 0.20) == pytest.approx(0.0, abs=1e-2)
    with pytest.raises(ValueError, match="Time to expiration \(T\) must be positive."):
        black_scholes_call_price(105, 100, 0, 0.05, 0.20)

def test_bsm_call_price_zero_volatility():
    """Test call price with zero volatility (should raise ValueError)."""
    # The _d1_d2 function correctly raises a ValueError for sigma <= 0
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        black_scholes_call_price(100, 100, 1.0, 0.05, 0)
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        black_scholes_call_price(105, 100, 1.0, 0.05, 0)
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        black_scholes_call_price(90, 100, 1.0, 0.05, 0)

def test_bsm_call_price_with_dividends():
    """Test call option price with a continuous dividend yield."""
    # S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02 (2% dividend)
    # Expected from code output: 9.227005508154036
    assert black_scholes_call_price(100, 100, 1.0, 0.05, 0.20, q=0.02) == pytest.approx(9.227, rel=1e-3)

def test_bsm_call_price_invalid_S():
    """Test call price with non-positive S."""
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive."):
        black_scholes_call_price(0, K_test, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive."):
        black_scholes_call_price(-10, K_test, T_test, r_test, sigma_test, q_test)

def test_bsm_call_price_invalid_K():
    """Test call price with non-positive K."""
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive."):
        black_scholes_call_price(S_test, 0, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive."):
        black_scholes_call_price(S_test, -10, T_test, r_test, sigma_test, q_test)


# --- black_scholes_put_price tests ---
def test_bsm_put_price_itm():
    """Test in-the-money put option price."""
    # S=90, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from code output: 10.214164528888958
    assert black_scholes_put_price(90, 100, 1.0, 0.05, 0.20) == pytest.approx(10.214, rel=1e-3)

def test_bsm_put_price_atm():
    """Test at-the-money put option price."""
    # S=100, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from code output: 5.573526022256971
    assert black_scholes_put_price(100, 100, 1.0, 0.05, 0.20) == pytest.approx(5.574, rel=1e-3)

def test_bsm_put_price_otm():
    """Test out-of-the-money put option price."""
    # S=110, K=100, T=1, r=0.05, sigma=0.2, q=0
    # Expected from code output: 2.785896190661841
    assert black_scholes_put_price(110, 100, 1.0, 0.05, 0.20) == pytest.approx(2.786, rel=1e-3)

def test_bsm_put_price_zero_time_to_expiration():
    """Test put price with zero time to expiration (should be max(0, K-S))."""
    assert black_scholes_put_price(95, 100, 0.0001, 0.05, 0.20) == pytest.approx(5.0, abs=1e-2)
    assert black_scholes_put_price(105, 100, 0.0001, 0.05, 0.20) == pytest.approx(0.0, abs=1e-2)
    with pytest.raises(ValueError, match="Time to expiration \(T\) must be positive."):
        black_scholes_put_price(95, 100, 0, 0.05, 0.20)

def test_bsm_put_price_zero_volatility():
    """Test put price with zero volatility (should raise ValueError)."""
    # The _d1_d2 function correctly raises a ValueError for sigma <= 0
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        black_scholes_put_price(100, 100, 1.0, 0.05, 0)
    with pytest.raises(ValueError, match="Volatility \(sigma\) must be positive."):
        black_scholes_put_price(90, 100, 1.0, 0.05, 0)

def test_bsm_put_price_with_dividends():
    """Test put option price with a continuous dividend yield."""
    # S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02 (2% dividend)
    # Expected from code output: 6.330080627549918
    assert black_scholes_put_price(100, 100, 1.0, 0.05, 0.20, q=0.02) == pytest.approx(6.330, rel=1e-3)

def test_bsm_put_price_invalid_S():
    """Test put price with non-positive S."""
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive."):
        black_scholes_put_price(0, K_test, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Current stock price \(S\) must be positive."):
        black_scholes_put_price(-10, K_test, T_test, r_test, sigma_test, q_test)

def test_bsm_put_price_invalid_K():
    """Test put price with non-positive K."""
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive."):
        black_scholes_put_price(S_test, 0, T_test, r_test, sigma_test, q_test)
    with pytest.raises(ValueError, match="Strike price \(K\) must be positive."):
        black_scholes_put_price(S_test, -10, T_test, r_test, sigma_test, q_test)