# tests/test_commodity_finance.py

import pytest
from mathematical_functions.commodity_finance import (
    calculate_commodity_futures_price_cost_of_carry,
    calculate_schwartz_smith_futures_price
)
import math

# --- Test Cases for calculate_commodity_futures_price_cost_of_carry ---

def test_futures_cost_of_carry_no_costs():
    """
    Test basic futures price with no storage costs or convenience yield.
    Should be F = S * exp(r * T)
    """
    S = 100.0
    T = 1.0
    r = 0.05
    expected_f = S * math.exp(r * T)
    result = calculate_commodity_futures_price_cost_of_carry(S, T, r)
    assert result == pytest.approx(expected_f)

def test_futures_cost_of_carry_with_storage():
    """
    Test futures price with positive storage cost. F = S * exp((r + u) * T)
    """
    S = 100.0
    T = 1.0
    r = 0.05
    storage_cost_rate = 0.02 # 2% continuous storage cost
    expected_f = S * math.exp((r + storage_cost_rate) * T)
    result = calculate_commodity_futures_price_cost_of_carry(S, T, r, storage_cost_rate=storage_cost_rate)
    assert result == pytest.approx(expected_f)

def test_futures_cost_of_carry_with_convenience_yield():
    """
    Test futures price with positive convenience yield. F = S * exp((r - y) * T)
    """
    S = 100.0
    T = 1.0
    r = 0.05
    convenience_yield_rate = 0.03 # 3% continuous convenience yield
    expected_f = S * math.exp((r - convenience_yield_rate) * T)
    result = calculate_commodity_futures_price_cost_of_carry(S, T, r, convenience_yield_rate=convenience_yield_rate)
    assert result == pytest.approx(expected_f)

def test_futures_cost_of_carry_with_both_costs():
    """
    Test futures price with both storage cost and convenience yield.
    F = S * exp((r + u - y) * T)
    """
    S = 100.0
    T = 1.0
    r = 0.05
    storage_cost_rate = 0.02
    convenience_yield_rate = 0.03
    expected_f = S * math.exp((r + storage_cost_rate - convenience_yield_rate) * T)
    result = calculate_commodity_futures_price_cost_of_carry(S, T, r, storage_cost_rate=storage_cost_rate, convenience_yield_rate=convenience_yield_rate)
    assert result == pytest.approx(expected_f)

def test_futures_cost_of_carry_zero_time():
    """
    Test with zero time to maturity. Futures price should equal spot price.
    """
    S = 100.0
    T = 1e-9 # Very small time approaching zero
    r = 0.05
    u = 0.02
    y = 0.03
    result = calculate_commodity_futures_price_cost_of_carry(S, T, r, u, y)
    assert result == pytest.approx(S)

def test_futures_cost_of_carry_invalid_S():
    with pytest.raises(ValueError, match="Current spot price \(S\) must be positive."):
        calculate_commodity_futures_price_cost_of_carry(0, 1.0, 0.05)

def test_futures_cost_of_carry_invalid_T():
    with pytest.raises(ValueError, match="Time to maturity \(T\) must be positive."):
        calculate_commodity_futures_price_cost_of_carry(100, 0, 0.05)

# --- Test Cases for calculate_schwartz_smith_futures_price ---

def test_schwartz_smith_futures_basic_sanity_check():
    """
    Test a basic scenario for Schwartz-Smith, ensuring a reasonable positive output.
    We set current_long_term_factor_Z to be log(S) assuming X_t=0 initially.
    """
    S = 50.0
    # Interpret current_long_term_factor_Z as Z_t (current log-level of the long-term factor)
    # If X_t is assumed to be 0 initially, then Z_t = ln(S)
    current_zeta_for_test = math.log(S) # Approx 3.912

    time_to_maturity = 0.5 # 6 months
    risk_free_rate = 0.03
    kappa = 0.5 # Moderate mean reversion for X_t
    sigma_X = 0.15 # Short-term volatility
    sigma_Zeta = 0.10 # Long-term volatility
    rho = 0.3 # Positive correlation

    result = calculate_schwartz_smith_futures_price(
        S, current_zeta_for_test, time_to_maturity, risk_free_rate,
        kappa, sigma_X, sigma_Zeta, rho
    )
    assert result > 0 # Futures price must be positive

    # Re-calculate the expected value with the corrected interpretation and formula:
    tau = time_to_maturity
    current_X = math.log(S) - current_zeta_for_test # This will be 0 if current_zeta_for_test = math.log(S)

    expected_X_T = current_X * math.exp(-kappa * tau)
    expected_Z_T = current_zeta_for_test + risk_free_rate * tau
    expected_log_S_T = expected_X_T + expected_Z_T

    var_X_T = (sigma_X**2 / (2 * kappa)) * (1 - math.exp(-2 * kappa * tau))
    var_Z_T = sigma_Zeta**2 * tau
    cov_X_Z_T = (rho * sigma_X * sigma_Zeta / kappa) * (1 - math.exp(-kappa * tau))
    total_variance_log_S_T = var_X_T + var_Z_T + 2 * cov_X_Z_T

    expected_log_futures_price = expected_log_S_T + 0.5 * total_variance_log_S_T
    expected_f = math.exp(expected_log_futures_price)

    # The expected_f should now be a reasonable value close to S (50.0) or slightly higher/lower based on parameters.
    # Let's calculate it manually to get the precise expected_f
    # S = 50.0
    # current_zeta_for_test = math.log(50.0) = 3.912023005428146
    # time_to_maturity = 0.5
    # risk_free_rate = 0.03
    # kappa = 0.5
    # sigma_X = 0.15
    # sigma_Zeta = 0.10
    # rho = 0.3

    # current_X = 3.912023005428146 - 3.912023005428146 = 0.0

    # expected_X_T = 0.0 * math.exp(-0.5 * 0.5) = 0.0
    # expected_Z_T = 3.912023005428146 + 0.03 * 0.5 = 3.912023005428146 + 0.015 = 3.927023005428146

    # expected_log_S_T = 0.0 + 3.927023005428146 = 3.927023005428146

    # var_X_T = (0.15**2 / (2 * 0.5)) * (1 - math.exp(-2 * 0.5 * 0.5))
    # var_X_T = (0.0225 / 1.0) * (1 - math.exp(-0.5)) = 0.0225 * (1 - 0.6065306597126334) = 0.00885306015646575

    # var_Z_T = 0.10**2 * 0.5 = 0.01 * 0.5 = 0.005

    # cov_X_Z_T = (0.3 * 0.15 * 0.10 / 0.5) * (1 - math.exp(-0.5 * 0.5))
    # cov_X_Z_T = (0.0045 / 0.5) * (1 - math.exp(-0.25)) = 0.009 * (1 - 0.7788007830714049) = 0.0019907929523573557

    # total_variance_log_S_T = 0.00885306015646575 + 0.005 + 2 * 0.0019907929523573557 = 0.01783464606118046

    # expected_log_futures_price = 3.927023005428146 + 0.5 * 0.01783464606118046
    # expected_log_futures_price = 3.927023005428146 + 0.00891732303059023 = 3.9359403284587364

    # expected_f = math.exp(3.9359403284587364) = 51.229158 (approx)

    assert result == pytest.approx(51.229158, rel=1e-3) # Use relative tolerance for floating point comparisons

# ... (rest of your existing tests for calculate_schwartz_smith_futures_price) ...

# Update the input argument name in other SS tests too for consistency
def test_schwartz_smith_futures_zero_time_to_maturity():
    S = 75.0
    current_zeta_for_test = math.log(S) # Z_t = ln(S) assuming X_t=0
    time_to_maturity = 1e-9 # Very small time approaching zero
    risk_free_rate = 0.04
    kappa = 0.8
    sigma_X = 0.20
    sigma_Zeta = 0.05
    rho = -0.5

    result = calculate_schwartz_smith_futures_price(
        S, current_zeta_for_test, time_to_maturity, risk_free_rate,
        kappa, sigma_X, sigma_Zeta, rho
    )
    assert result == pytest.approx(S, rel=1e-3) # Should be very close to S

def test_schwartz_smith_futures_zero_volatility():
    S = 100.0
    current_zeta_for_test = math.log(S) # Z_t = ln(S) assuming X_t=0
    time_to_maturity = 1.0
    risk_free_rate = 0.05
    kappa = 0.5
    sigma_X = 0.0 # No short-term vol
    sigma_Zeta = 0.0 # No long-term vol
    rho = 0.0 # No correlation

    result = calculate_schwartz_smith_futures_price(
        S, current_zeta_for_test, time_to_maturity, risk_free_rate,
        kappa, sigma_X, sigma_Zeta, rho
    )

    # Recalculate expected_f for this scenario with 0 volatility
    # If sigma_X and sigma_Zeta are 0, then var_X_T, var_Z_T, cov_X_Z_T are 0.
    # total_variance_log_S_T = 0
    # current_X = math.log(S) - current_zeta_for_test = 0
    # expected_X_T = 0
    # expected_Z_T = current_zeta_for_test + risk_free_rate * tau
    # expected_log_S_T = expected_Z_T = current_zeta_for_test + risk_free_rate * tau
    # log_futures_price = expected_log_S_T
    expected_f = math.exp(current_zeta_for_test + risk_free_rate * time_to_maturity)
    assert result == pytest.approx(expected_f, abs=1e-6)


def test_schwartz_smith_futures_varying_correlation():
    S = 100.0
    current_zeta_for_test = math.log(S) # Z_t = ln(S) assuming X_t=0
    time_to_maturity = 1.0
    risk_free_rate = 0.05
    kappa = 0.5
    sigma_X = 0.20
    sigma_Zeta = 0.10

    # Test with negative rho
    rho_neg = -0.8
    f_neg_rho = calculate_schwartz_smith_futures_price(
        S, current_zeta_for_test, time_to_maturity, risk_free_rate,
        kappa, sigma_X, sigma_Zeta, rho_neg
    )

    # Test with positive rho
    rho_pos = 0.8
    f_pos_rho = calculate_schwartz_smith_futures_price(
        S, current_zeta_for_test, time_to_maturity, risk_free_rate,
        kappa, sigma_X, sigma_Zeta, rho_pos
    )

    assert f_pos_rho > f_neg_rho


# --- Test Cases for Input Validation (Schwartz-Smith) ---
# Update argument name here too
def test_schwartz_smith_invalid_S():
    with pytest.raises(ValueError, match="Current spot price \(S\) must be positive."):
        calculate_schwartz_smith_futures_price(0, math.log(50), 1, 0.05, 0.5, 0.1, 0.05, 0.3)

def test_schwartz_smith_invalid_time_to_maturity():
    with pytest.raises(ValueError, match="Time to maturity must be positive."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 0, 0.05, 0.5, 0.1, 0.05, 0.3)

# No direct validation for current_long_term_factor_Z being positive, as it's a log value
# The error "Long-term mean reversion level must be positive." from original code is removed.
# However, if it's too far off, ln(S) - Z_t might cause issues or results in extreme values.

def test_schwartz_smith_invalid_kappa():
    with pytest.raises(ValueError, match="Mean reversion rate \(kappa\) must be positive."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 1, 0.05, 0, 0.1, 0.05, 0.3)

def test_schwartz_smith_invalid_sigma_X_negative():
    with pytest.raises(ValueError, match="Volatilities \(sigma_X, sigma_Zeta\) cannot be negative."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 1, 0.05, 0.5, -0.1, 0.05, 0.3)

def test_schwartz_smith_invalid_sigma_Zeta_negative():
    with pytest.raises(ValueError, match="Volatilities \(sigma_X, sigma_Zeta\) cannot be negative."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 1, 0.05, 0.5, 0.1, -0.05, 0.3)

def test_schwartz_smith_invalid_rho_too_low():
    with pytest.raises(ValueError, match="Correlation \(rho\) must be between -1 and 1."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 1, 0.05, 0.5, 0.1, 0.05, -1.1)

def test_schwartz_smith_invalid_rho_too_high():
    with pytest.raises(ValueError, match="Correlation \(rho\) must be between -1 and 1."):
        calculate_schwartz_smith_futures_price(50, math.log(50), 1, 0.05, 0.5, 0.1, 0.05, 1.1)
