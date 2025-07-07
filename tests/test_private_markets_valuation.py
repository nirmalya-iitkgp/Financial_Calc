# tests/test_private_markets_valuation.py

import pytest
import math
import numpy as np
from mathematical_functions.private_markets_valuation import (
    calculate_illiquidity_discount_option_model,
    calculate_real_estate_terminal_value_gordon_growth,
    simulate_private_equity_valuation_monte_carlo
)
from scipy.stats import norm # For comparison with BSM if applicable


# --- Test Cases for calculate_illiquidity_discount_option_model ---

def test_illiquidity_discount_option_model_basic():
    """
    Test a basic scenario for the illiquidity discount model.
    Expected values are derived from manual calculation or known benchmarks.
    """
    asset_value = 100.0
    liquidation_cost_pct = 0.10 # 10% immediate cost
    holding_period = 2.0 # 2 years
    volatility = 0.25 # 25% annual volatility
    risk_free_rate = 0.05
    g_spread = 0.01 # 1% additional illiquidity premium

    result = calculate_illiquidity_discount_option_model(
        asset_value, liquidation_cost_pct, holding_period,
        volatility, risk_free_rate, g_spread
    )

    # Manual verification for a rough estimate:
    # K_immediate = 100 * (1 - 0.1) = 90
    # r_eff = 0.05 + 0.01 = 0.06
    # BSM Put(S=100, K=90, T=2, r=0.06, sigma=0.25, q=0)
    # d1 = (ln(100/90) + (0.06 + 0.5*0.25^2)*2) / (0.25*sqrt(2)) = (0.10536 + (0.06 + 0.03125)*2) / 0.35355 = (0.10536 + 0.1825) / 0.35355 = 0.28786 / 0.35355 = 0.8142
    # d2 = 0.8142 - 0.35355 = 0.46065
    # N(-d1) = N(-0.8142) = 1 - N(0.8142) = 1 - 0.7922 = 0.2078
    # N(-d2) = N(-0.46065) = 1 - N(0.46065) = 1 - 0.6775 = 0.3225
    # Put = 90 * exp(-0.06*2) * 0.3225 - 100 * 0.2078 = 90 * 0.8869 * 0.3225 - 20.78 = 25.75 - 20.78 = 4.97
    # So the illiquidity discount value should be around 4.97.

    assert result['illiquidity_discount_value'] == pytest.approx(4.97, abs=0.01)
    assert result['illiquidity_discount_pct'] == pytest.approx(4.97 / 100.0, abs=0.0001)
    assert result['adjusted_asset_value'] == pytest.approx(100.0 - 4.97, abs=0.01)
    assert result['illiquidity_discount_value'] > 0
    assert 0 < result['illiquidity_discount_pct'] < 1


def test_illiquidity_discount_option_model_zero_liquidation_cost():
    """
    Test when immediate liquidation cost is zero. Illiquidity still has a value due to holding period.
    """
    asset_value = 100.0
    liquidation_cost_pct = 0.0
    holding_period = 1.0
    volatility = 0.30
    risk_free_rate = 0.05

    result = calculate_illiquidity_discount_option_model(
        asset_value, liquidation_cost_pct, holding_period,
        volatility, risk_free_rate
    )
    # With 0 liquidation cost, the "strike" is 100.0. A put on 100 with strike 100 will have some value.
    # BSM Put(S=100, K=100, T=1, r=0.05, sigma=0.30, q=0) ~ 8.026 - 5 + 100*(1-exp(-0.05)) ~ 8.026-5+4.87 = 7.89 Put is 7.97.
    # d1 = (ln(100/100) + (0.05 + 0.5*0.30^2)*1) / (0.30*sqrt(1)) = (0 + (0.05 + 0.045)*1) / 0.30 = 0.095 / 0.30 = 0.3167
    # d2 = 0.3167 - 0.30 = 0.0167
    # N(-d1) = 1-N(0.3167) = 1-0.6242 = 0.3758
    # N(-d2) = 1-N(0.0167) = 1-0.5067 = 0.4933
    # Put = 100*exp(-0.05*1)*0.4933 - 100*0.3758 = 100*0.9512*0.4933 - 37.58 = 46.91 - 37.58 = 9.33
    # This is effectively the value of the put that gives the holder the right to sell at asset_value if it drops.
    # The discount reflects the cost of not being able to sell immediately at market.
    assert result['illiquidity_discount_value'] == pytest.approx(9.354, abs=0.001) # Increased precision for test
    assert result['illiquidity_discount_value'] > 0

def test_illiquidity_discount_option_model_high_volatility():
    """
    Test that higher volatility increases the illiquidity discount (put value increases with vol).
    """
    base_params = {
        'asset_value': 100.0, 'liquidation_cost_pct': 0.05,
        'holding_period': 1.0, 'risk_free_rate': 0.05, 'g_spread': 0.0
    }
    
    low_vol_result = calculate_illiquidity_discount_option_model(**base_params, volatility=0.10)
    high_vol_result = calculate_illiquidity_discount_option_model(**base_params, volatility=0.50)

    assert high_vol_result['illiquidity_discount_value'] > low_vol_result['illiquidity_discount_value']

def test_illiquidity_discount_option_model_invalid_inputs():
    with pytest.raises(ValueError, match="Asset value must be positive."):
        calculate_illiquidity_discount_option_model(0, 0.1, 1.0, 0.2, 0.05)
    with pytest.raises(ValueError, match="Liquidation cost percentage"):
        calculate_illiquidity_discount_option_model(100, 1.0, 1.0, 0.2, 0.05)
    with pytest.raises(ValueError, match="Holding period must be positive."):
        calculate_illiquidity_discount_option_model(100, 0.1, 0, 0.2, 0.05)
    with pytest.raises(ValueError, match="Volatility must be positive."):
        calculate_illiquidity_discount_option_model(100, 0.1, 1.0, 0, 0.05)
    with pytest.raises(ValueError, match="G-spread cannot be negative."):
        calculate_illiquidity_discount_option_model(100, 0.1, 1.0, 0.2, 0.05, -0.01)

# --- Test Cases for calculate_real_estate_terminal_value_gordon_growth ---

def test_terminal_value_gordon_growth_basic():
    """
    Test a basic Gordon Growth Model calculation for terminal value.
    """
    noi_next_period = 100_000 # $100k
    exit_cap_rate = 0.08 # 8%
    long_term_growth_rate = 0.03 # 3%

    expected_tv = 100_000 / (0.08 - 0.03) # 100,000 / 0.05 = 2,000,000
    result = calculate_real_estate_terminal_value_gordon_growth(
        noi_next_period, exit_cap_rate, long_term_growth_rate
    )
    assert result == pytest.approx(expected_tv)

def test_terminal_value_gordon_growth_high_growth():
    """
    Test when growth rate is close to cap rate, leading to a very high terminal value.
    """
    noi_next_period = 50_000
    exit_cap_rate = 0.06
    long_term_growth_rate = 0.055 # Very close to cap rate

    expected_tv = 50_000 / (0.06 - 0.055) # 50,000 / 0.005 = 10,000,000
    result = calculate_real_estate_terminal_value_gordon_growth(
        noi_next_period, exit_cap_rate, long_term_growth_rate
    )
    assert result == pytest.approx(expected_tv)

def test_terminal_value_gordon_growth_invalid_inputs():
    with pytest.raises(ValueError, match="Net Operating Income \(NOI\) for the next period must be positive."):
        calculate_real_estate_terminal_value_gordon_growth(0, 0.08, 0.03)
    with pytest.raises(ValueError, match="Exit capitalization rate must be positive."):
        calculate_real_estate_terminal_value_gordon_growth(100_000, 0, 0.03)
    with pytest.raises(ValueError, match="Long-term growth rate must be less than the exit capitalization rate."):
        calculate_real_estate_terminal_value_gordon_growth(100_000, 0.08, 0.08) # Equal
    with pytest.raises(ValueError, match="Long-term growth rate must be less than the exit capitalization rate."):
        calculate_real_estate_terminal_value_gordon_growth(100_000, 0.08, 0.10) # Greater

# --- Test Cases for simulate_private_equity_valuation_monte_carlo ---

def test_private_equity_monte_carlo_sanity_check():
    """
    Test a basic Monte Carlo simulation for PE valuation for general sanity.
    Ensure output is positive and percentiles are logically ordered.
    """
    base_fcf = [10, 20, 30, 40, 50]
    term_growth_mean = 0.02
    term_growth_std = 0.005
    disc_rate_mean = 0.10
    disc_rate_std = 0.01
    exit_mult_mean = 8.0
    exit_mult_std = 0.5
    num_sims = 10000
    exit_year = 5 # Exit at end of forecast period

    result = simulate_private_equity_valuation_monte_carlo(
        base_fcf, term_growth_mean, term_growth_std, disc_rate_mean,
        disc_rate_std, exit_mult_mean, exit_mult_std, num_sims, exit_year, seed=42
    )

    assert 'simulated_valuations' in result
    assert isinstance(result['simulated_valuations'], np.ndarray)
    assert len(result['simulated_valuations']) == num_sims
    assert np.all(result['simulated_valuations'] > 0) # Valuations should be positive

    assert result['mean_valuation'] > 0
    assert result['median_valuation'] > 0
    assert result['valuation_percentiles']['5th'] < result['valuation_percentiles']['25th']
    assert result['valuation_percentiles']['25th'] < result['median_valuation']
    assert result['median_valuation'] < result['valuation_percentiles']['75th']
    assert result['valuation_percentiles']['75th'] < result['valuation_percentiles']['95th']
    
    # Example expected range for a sanity check (very rough estimate for these inputs):
    # Base valuation: PV of FCFs + PV of TV (50 * 8 = 400 discounted)
    # Roughly: (10/1.1 + 20/1.1^2 + 30/1.1^3 + 40/1.1^4 + 50/1.1^5) + 400/1.1^5
    # ~ (9.09 + 16.53 + 22.54 + 27.32 + 31.05) + 248.37 = 106.53 + 248.37 = 354.9
    assert result['mean_valuation'] == pytest.approx(354.9, abs=50) # Allowing larger error due to MC variance

def test_private_equity_monte_carlo_reproducibility():
    """
    Test that Monte Carlo results are identical for the same seed.
    """
    base_fcf = [10, 20, 30]
    common_params = {
        'terminal_value_growth_rate_mean': 0.02, 'terminal_value_growth_rate_std': 0.005,
        'discount_rate_mean': 0.10, 'discount_rate_std': 0.01,
        'exit_multiple_mean': 8.0, 'exit_multiple_std': 0.5,
        'num_simulations': 1000, 'exit_year': 3
    }
    
    result1 = simulate_private_equity_valuation_monte_carlo(base_fcf, **common_params, seed=123)
    result2 = simulate_private_equity_valuation_monte_carlo(base_fcf, **common_params, seed=123)
    result3 = simulate_private_equity_valuation_monte_carlo(base_fcf, **common_params, seed=456)

    assert result1['mean_valuation'] == pytest.approx(result2['mean_valuation'])
    assert np.array_equal(result1['simulated_valuations'], result2['simulated_valuations']) # Exact array equality

    assert result1['mean_valuation'] != pytest.approx(result3['mean_valuation']) # Different seed, different result

def test_private_equity_monte_carlo_zero_std_dev():
    """
    Test when all standard deviations are zero, result should be deterministic.
    """
    base_fcf = [100]
    term_growth_mean = 0.02
    term_growth_std = 0.0
    disc_rate_mean = 0.10
    disc_rate_std = 0.0
    exit_mult_mean = 10.0
    exit_mult_std = 0.0
    num_sims = 100
    exit_year = 1 # Exit at end of year 1

    result = simulate_private_equity_valuation_monte_carlo(
        base_fcf, term_growth_mean, term_growth_std, disc_rate_mean,
        disc_rate_std, exit_mult_mean, exit_mult_std, num_sims, exit_year
    )

    # Calculate expected deterministic value:
    # PV of FCF[0] = 100 / (1 + 0.10)^1 = 90.909
    # Terminal Value = FCF[0] * Exit_Multiple = 100 * 10 = 1000 (using multiple directly on last FCF)
    # PV of TV = 1000 / (1 + 0.10)^1 = 909.091
    # Total Valuation = 90.909 + 909.091 = 1000.0
    
    # Note: Our TV calculation logic in simulate_private_equity_valuation_monte_carlo is
    # `terminal_value = terminal_value_multiple` if `exit_year <= num_forecast_years`.
    # So it uses 100 * 10 = 1000.
    
    expected_valuation = base_fcf[0] / (1 + disc_rate_mean) + \
                         (base_fcf[0] * exit_mult_mean) / (1 + disc_rate_mean)

    assert result['mean_valuation'] == pytest.approx(expected_valuation)
    assert result['median_valuation'] == pytest.approx(expected_valuation)
    assert result['valuation_percentiles']['5th'] == pytest.approx(expected_valuation)
    assert result['valuation_percentiles']['95th'] == pytest.approx(expected_valuation)


def test_private_equity_monte_carlo_invalid_inputs():
    with pytest.raises(ValueError, match="base_free_cash_flows must be a list of numbers."):
        simulate_private_equity_valuation_monte_carlo(
            "not a list", 0.02, 0.005, 0.10, 0.01, 8.0, 0.5, 1000, 3
        )
    with pytest.raises(ValueError, match="Number of simulations must be a positive integer."):
        simulate_private_equity_valuation_monte_carlo(
            [10, 20], 0.02, 0.005, 0.10, 0.01, 8.0, 0.5, 0, 2
        )
    with pytest.raises(ValueError, match="Exit year must be a positive integer within the plausible range of forecast period."):
        simulate_private_equity_valuation_monte_carlo(
            [10, 20], 0.02, 0.005, 0.10, 0.01, 8.0, 0.5, 1000, 0 # exit_year 0
        )
    with pytest.raises(ValueError, match="Exit year must be a positive integer within the plausible range of forecast period."):
        simulate_private_equity_valuation_monte_carlo(
            [10, 20], 0.02, 0.005, 0.10, 0.01, 8.0, 0.5, 1000, 4 # FCFs for 2 years, exit_year 4 is too far
        )
    with pytest.raises(ValueError, match="Standard deviations cannot be negative."):
        simulate_private_equity_valuation_monte_carlo(
            [10, 20], 0.02, -0.005, 0.10, 0.01, 8.0, 0.5, 1000, 2
        )
    with pytest.raises(ValueError, match="Seed must be an integer or None."):
        simulate_private_equity_valuation_monte_carlo(
            [10, 20], 0.02, 0.005, 0.10, 0.01, 8.0, 0.5, 1000, 2, seed="invalid"
        )