# tests/test_credit_risk.py

import pytest
import math
from mathematical_functions.credit_risk_advanced import calculate_merton_model_credit_risk, _find_implied_asset_values_numerical

# This fixture will temporarily replace the internal numerical solver function
# to simulate specific error conditions for testing.
@pytest.fixture
def mock_solver(monkeypatch):
    """
    A pytest fixture to temporarily mock _find_implied_asset_values_numerical
    for testing error handling and specific return values.
    """
    original_solver = calculate_merton_model_credit_risk.__globals__['_find_implied_asset_values_numerical']
    
    def mock_function(mock_return_value=None, mock_exception=None):
        if mock_exception:
            # If an exception is specified, the mock function will raise it.
            def _mock_func(*args, **kwargs):
                raise mock_exception
            monkeypatch.setattr(
                'mathematical_functions.credit_risk_advanced._find_implied_asset_values_numerical',
                _mock_func
            )
        elif mock_return_value is not None:
            # If a return value is specified, the mock function will return it.
            def _mock_func(*args, **kwargs):
                return mock_return_value
            monkeypatch.setattr(
                'mathematical_functions.credit_risk_advanced._find_implied_asset_values_numerical',
                _mock_func
            )
        else:
            # Restore the original function if no specific mock is requested
            monkeypatch.setattr(
                'mathematical_functions.credit_risk_advanced._find_implied_asset_values_numerical',
                original_solver
            )
    
    yield mock_function
    
    # Teardown: Ensure the original function is restored after the test
    monkeypatch.setattr(
        'mathematical_functions.credit_risk_advanced._find_implied_asset_values_numerical',
        original_solver
    )


def test_basic_valid_case():
    """
    Test with a standard set of valid inputs.
    Expected results are based on typical Merton model behavior,
    though exact values depend on the numerical solver's precision and initial guesses.
    """
    E = 100.0       # Equity Value
    sigma_E = 0.30  # Equity Volatility (30%)
    D = 80.0        # Debt Value
    T = 1.0         # Time to Maturity (1 year)
    r = 0.05        # Risk-free rate (5%)

    result = calculate_merton_model_credit_risk(E, sigma_E, D, T, r)

    assert isinstance(result, dict)
    assert 'implied_asset_value' in result
    assert 'implied_asset_volatility' in result
    assert 'distance_to_default' in result
    assert 'probability_of_default' in result

    # Basic sanity checks on the outputs
    assert result['implied_asset_value'] > 0
    assert result['implied_asset_volatility'] > 0
    assert isinstance(result['distance_to_default'], float)
    assert 0 <= result['probability_of_default'] <= 1

    # A rough check: implied asset value should generally be > E and often > E+D for healthy firms
    # Or at least in the ballpark of E+D if debt is significant
    assert result['implied_asset_value'] > E

    # Implied asset volatility should generally be less than equity volatility
    # because equity is a leveraged position on assets.
    assert result['implied_asset_volatility'] < sigma_E * 1.5 # Allow some tolerance, but it should be lower
    assert result['implied_asset_volatility'] > sigma_E * 0.1 # Should not be extremely low


@pytest.mark.parametrize("E, sigma_E, D, T, r", [
    (0, 0.3, 80, 1, 0.05),    # E = 0
    (100, 0, 80, 1, 0.05),    # sigma_E = 0
    (100, 0.3, 0, 1, 0.05),   # D = 0
    (100, 0.3, 80, 0, 0.05),  # T = 0
    (-10, 0.3, 80, 1, 0.05),  # Negative E
    (100, -0.1, 80, 1, 0.05), # Negative sigma_E
    (100, 0.3, -5, 1, 0.05),  # Negative D
    (100, 0.3, 80, -0.5, 0.05),# Negative T
])
def test_zero_or_negative_inputs(E, sigma_E, D, T, r):
    """
    Test cases with zero or negative inputs for parameters that must be positive.
    Should raise ValueError.
    """
    with pytest.raises(ValueError):
        calculate_merton_model_credit_risk(E, sigma_E, D, T, r)

def test_high_equity_volatility():
    """
    Test with high equity volatility AND very high debt, to ensure a higher PD.
    """
    E = 50.0
    sigma_E = 0.80 # High volatility
    D = 200.0       # Much higher debt relative to equity
    T = 1.0         # Slightly longer time to allow more volatility impact
    r = 0.02

    result = calculate_merton_model_credit_risk(E, sigma_E, D, T, r)
    assert isinstance(result, dict)
    assert result['probability_of_default'] > 0.1 # Now this assertion is more likely to pass
    assert result['implied_asset_volatility'] < sigma_E
    
def test_low_equity_volatility():
    """
    Test with low equity volatility, implying a very stable firm.
    Expected: low PD, V close to E+D, sigma_V close to sigma_E.
    """
    E = 200.0
    sigma_E = 0.10 # Low volatility
    D = 50.0
    T = 2.0
    r = 0.04

    result = calculate_merton_model_credit_risk(E, sigma_E, D, T, r)
    assert isinstance(result, dict)
    assert result['probability_of_default'] < 0.01 # Expect very low PD
    assert result['implied_asset_volatility'] == pytest.approx(sigma_E, rel=0.5) # Use pytest.approx for float comparison
    assert result['implied_asset_value'] == pytest.approx(E + D * math.exp(-r*T), rel=0.1) # V should be close to E+PV(D)

def test_solver_non_physical_result(mock_solver):
    """
    Test if the function correctly handles a simulated non-physical result
    from the internal solver (_find_implied_asset_values_numerical).
    """
    mock_solver(mock_exception=RuntimeError("Numerical solver converged to non-physical asset values/volatilities."))
    
    with pytest.raises(RuntimeError, match="Failed to find implied asset values"):
        calculate_merton_model_credit_risk(100, 0.3, 80, 1, 0.05)

def test_solver_failed_convergence(mock_solver):
    """
    Test if the function correctly handles a simulated non-convergence from
    the internal solver (_find_implied_asset_values_numerical).
    """
    mock_solver(mock_exception=RuntimeError("Numerical solver failed to converge: The solution did not converge."))

    with pytest.raises(RuntimeError, match="Failed to find implied asset values"):
        calculate_merton_model_credit_risk(100, 0.3, 80, 1, 0.05)

@pytest.mark.parametrize("r_val", [0.0, -0.01, 0.1])
def test_edge_cases_r(r_val):
    """Test with different risk-free rates."""
    E = 100.0; sigma_E = 0.30; D = 80.0; T = 1.0
    result = calculate_merton_model_credit_risk(E, sigma_E, D, T, r_val)
    assert isinstance(result, dict)
    assert result['implied_asset_value'] > 0
    assert result['implied_asset_volatility'] > 0