# tests/test_portfolio_management.py

import pytest
from mathematical_functions.portfolio_management import (
    calculate_capm_return,
    fama_french_3_factor_expected_return,
    fama_french_5_factor_expected_return,
    calculate_sharpe_ratio
)

# --- Tests for calculate_capm_return ---

def test_capm_return_basic():
    """
    Test CAPM calculation with typical, positive values.
    Expected Return = Risk-Free Rate + Beta * Market Risk Premium
    0.03 + 1.2 * 0.07 = 0.03 + 0.084 = 0.114 (11.4%)
    """
    assert calculate_capm_return(0.03, 0.07, 1.2) == pytest.approx(0.114)

def test_capm_return_beta_one():
    """
    Test CAPM when beta is 1.0.
    In this case, the expected return should equal the market's expected return (Rf + Market Risk Premium).
    0.03 + 1.0 * 0.07 = 0.03 + 0.07 = 0.10 (10%)
    """
    assert calculate_capm_return(0.03, 0.07, 1.0) == pytest.approx(0.03 + 0.07)

def test_capm_return_beta_zero():
    """
    Test CAPM when beta is 0.0 (a risk-free asset).
    The expected return should simply be the risk-free rate.
    0.03 + 0.0 * 0.07 = 0.03 (3%)
    """
    assert calculate_capm_return(0.03, 0.07, 0.0) == pytest.approx(0.03)

def test_capm_return_negative_beta():
    """
    Test CAPM with a negative beta, indicating a defensive asset or short position.
    0.03 + (-0.5) * 0.07 = 0.03 - 0.035 = -0.005 (-0.5%)
    """
    assert calculate_capm_return(0.03, 0.07, -0.5) == pytest.approx(-0.005)

def test_capm_return_zero_market_premium():
    """
    Test CAPM when the market risk premium is zero.
    The expected return should revert to the risk-free rate, regardless of beta.
    0.03 + 1.2 * 0.0 = 0.03 (3%)
    """
    assert calculate_capm_return(0.03, 0.0, 1.2) == pytest.approx(0.03)

# --- Tests for fama_french_3_factor_expected_return ---

def test_fama_french_3_factor_basic():
    """
    Test Fama-French 3-Factor model with typical inputs and non-zero betas.
    Expected Return = Rf + Beta_Mkt*Mkt_Excess + Beta_SMB*SMB_Ret + Beta_HML*HML_Ret
    0.03 + 1.0*0.07 + 0.5*0.03 + 0.4*0.02
    = 0.03 + 0.07 + 0.015 + 0.008 = 0.123 (12.3%)
    """
    assert fama_french_3_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=1.0,
        smb_beta=0.5,
        hml_beta=0.4,
        market_excess_return=0.07,
        smb_return=0.03,
        hml_return=0.02
    ) == pytest.approx(0.123)

@pytest.mark.parametrize("mkt_beta, smb_beta, hml_beta, mkt_return, smb_return, hml_return, expected_return", [
    (0.0, 0.0, 0.0, 0.07, 0.03, 0.02, 0.03), # All betas are zero, expected return should be risk-free rate
    (1.0, 0.0, 0.0, 0.07, 0.0, 0.0, 0.03 + 1.0 * 0.07) # Only market factor active, others zero (like CAPM)
])
def test_fama_french_3_factor_zero_conditions(mkt_beta, smb_beta, hml_beta, mkt_return, smb_return, hml_return, expected_return):
    """
    Test Fama-French 3-Factor with various zero conditions for betas or factor returns.
    Ensures that if all factors (or their betas) are zero, the expected return defaults to the risk-free rate,
    or behaves as CAPM if only market factor is active and others are zero.
    """
    assert fama_french_3_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=mkt_beta,
        smb_beta=smb_beta,
        hml_beta=hml_beta,
        market_excess_return=mkt_return,
        smb_return=smb_return,
        hml_return=hml_return
    ) == pytest.approx(expected_return)

def test_fama_french_3_factor_negative_returns_and_betas():
    """
    Test Fama-French 3-Factor with negative factor returns and betas to ensure correct calculation.
    0.03 + (1.0 * -0.05) + (-0.2 * 0.01) + (0.1 * -0.02)
    = 0.03 - 0.05 - 0.002 - 0.002 = -0.024 (-2.4%)
    """
    assert fama_french_3_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=1.0,
        smb_beta=-0.2,
        hml_beta=0.1,
        market_excess_return=-0.05,
        smb_return=0.01,
        hml_return=-0.02
    ) == pytest.approx(-0.024)

# --- Tests for fama_french_5_factor_expected_return ---

def test_fama_french_5_factor_basic():
    """
    Test Fama-French 5-Factor model with typical inputs and non-zero betas.
    Expected Return = Rf + Beta_Mkt*Mkt_Excess + Beta_SMB*SMB_Ret + Beta_HML*HML_Ret +
                      Beta_RMW*RMW_Ret + Beta_CMA*CMA_Ret
    0.03 + (1.0*0.07) + (0.5*0.03) + (0.4*0.02) + (0.3*0.01) + (0.2*0.015)
    = 0.03 + 0.07 + 0.015 + 0.008 + 0.003 + 0.003 = 0.129 (12.9%)
    """
    assert fama_french_5_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=1.0,
        smb_beta=0.5,
        hml_beta=0.4,
        rmw_beta=0.3,
        cma_beta=0.2,
        market_excess_return=0.07,
        smb_return=0.03,
        hml_return=0.02,
        rmw_return=0.01,
        cma_return=0.015
    ) == pytest.approx(0.129)

@pytest.mark.parametrize(
    "mkt_beta, smb_beta, hml_beta, rmw_beta, cma_beta, "
    "mkt_return, smb_return, hml_return, rmw_return, cma_return, expected_return",
    [
        # All betas are zero, expected return should be risk-free rate
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.07, 0.03, 0.02, 0.01, 0.015, 0.03),
        # All factor returns are zero, expected return should be risk-free rate
        (1.0, 0.5, 0.4, 0.3, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03)
    ]
)
def test_fama_french_5_factor_zero_conditions(
    mkt_beta, smb_beta, hml_beta, rmw_beta, cma_beta,
    mkt_return, smb_return, hml_return, rmw_return, cma_return, expected_return
):
    """
    Test Fama-French 5-Factor with various zero conditions for betas or factor returns.
    Ensures that if all factors (or their betas) are zero, the expected return defaults to the risk-free rate.
    """
    assert fama_french_5_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=mkt_beta,
        smb_beta=smb_beta,
        hml_beta=hml_beta,
        rmw_beta=rmw_beta,
        cma_beta=cma_beta,
        market_excess_return=mkt_return,
        smb_return=smb_return,
        hml_return=hml_return,
        rmw_return=rmw_return,
        cma_return=cma_return
    ) == pytest.approx(expected_return)

def test_fama_french_5_factor_negative_returns_and_betas():
    """
    Test Fama-French 5-Factor with negative factor returns and betas.
    0.03 + (1.0 * -0.05) + (-0.2 * 0.01) + (0.1 * -0.02) + (0.05 * -0.005) + (-0.1 * 0.003)
    = 0.03 - 0.05 - 0.002 - 0.002 - 0.00025 - 0.0003 = -0.02455 (-2.455%)
    """
    assert fama_french_5_factor_expected_return(
        risk_free_rate=0.03,
        market_beta=1.0,
        smb_beta=-0.2,
        hml_beta=0.1,
        rmw_beta=0.05,
        cma_beta=-0.1,
        market_excess_return=-0.05,
        smb_return=0.01,
        hml_return=-0.02,
        rmw_return=-0.005,
        cma_return=0.003
    ) == pytest.approx(-0.02455)


# --- Tests for calculate_sharpe_ratio ---

def test_sharpe_ratio_basic():
    """
    Test Sharpe Ratio calculation with a positive excess return.
    (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation
    (0.10 - 0.03) / 0.15 = 0.07 / 0.15 = 0.4666...
    """
    assert calculate_sharpe_ratio(0.10, 0.03, 0.15) == pytest.approx(0.466666, rel=1e-5)

def test_sharpe_ratio_negative_excess_return():
    """
    Test Sharpe Ratio with a negative excess return.
    (0.05 - 0.08) / 0.10 = -0.03 / 0.10 = -0.3
    """
    assert calculate_sharpe_ratio(0.05, 0.08, 0.10) == pytest.approx(-0.3)

@pytest.mark.parametrize("invalid_stdev", [0.0, -0.10, -1.0])
def test_sharpe_ratio_invalid_stdev(invalid_stdev):
    """
    Test Sharpe Ratio with zero or negative portfolio standard deviation.
    A ValueError should be raised because standard deviation must be positive for the calculation.
    The `match` argument ensures the specific error message is checked.
    """
    with pytest.raises(ValueError, match="Portfolio standard deviation must be positive to calculate Sharpe Ratio."):
        calculate_sharpe_ratio(0.10, 0.03, invalid_stdev)

def test_sharpe_ratio_risk_free_equal_portfolio_return():
    """
    Test Sharpe Ratio when the portfolio return equals the risk-free rate.
    The excess return is zero, so the Sharpe Ratio should be 0.
    (0.05 - 0.05) / 0.10 = 0.0 / 0.10 = 0.0
    """
    assert calculate_sharpe_ratio(0.05, 0.05, 0.10) == pytest.approx(0.0)

def test_sharpe_ratio_large_values():
    """
    Test Sharpe Ratio with larger or more extreme values to ensure robustness.
    (0.50 - 0.01) / 0.20 = 0.49 / 0.20 = 2.45
    """
    assert calculate_sharpe_ratio(0.50, 0.01, 0.20) == pytest.approx(2.45)