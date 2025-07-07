# tests/test_yield_curve_models.py

import pytest
import numpy as np
import math
from scipy.interpolate import CubicSpline

# Import the functions from the mathematical_functions package
from mathematical_functions.yield_curve_models import (
    _nelson_siegel_spot_yield_formula,
    _nelson_siegel_objective_function,
    fit_nelson_siegel_curve,
    get_nelson_siegel_spot_yield_curve,
    _svensson_spot_yield_formula,
    _svensson_objective_function,
    fit_svensson_curve,
    get_svensson_spot_yield_curve,
    fit_cubic_spline_curve,
    get_cubic_spline_spot_yield_curve
)

# --- Test Data for Yield Curve Models ---

# A simple, upward-sloping yield curve for testing
# Maturities in years, Yields as decimals
TEST_MATURITIES = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0])
TEST_YIELDS_UPWARD = np.array([0.02, 0.025, 0.03, 0.035, 0.04, 0.042, 0.045, 0.047, 0.048, 0.049])

# A more complex curve shape (e.g., inverted or humped) for robust testing
TEST_MATURITIES_COMPLEX = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
TEST_YIELDS_COMPLEX = np.array([0.05, 0.048, 0.045, 0.040, 0.038, 0.039, 0.041, 0.043])

# --- Nelson-Siegel Model Tests ---

# Test helper function: _nelson_siegel_spot_yield_formula
def test_nelson_siegel_spot_yield_formula_basic():
    # Test with known parameters and maturity
    # Values chosen to make calculations straightforward
    # m=1, beta0=0.01, beta1=0.01, beta2=0.01, tau=1.0
    # Expected: 0.01 + 0.01*( (1-e^-1)/1 ) + 0.01*( (1-e^-1)/1 - e^-1 )
    #           0.01 + 0.01*(0.6321) + 0.01*(0.6321 - 0.3679)
    #           0.01 + 0.006321 + 0.002642 = 0.018963
    expected_yield = 0.01 + 0.01 * ((1 - math.exp(-1/1.0))/(1/1.0)) + \
                     0.01 * (((1 - math.exp(-1/1.0))/(1/1.0)) - math.exp(-1/1.0))
    assert math.isclose(_nelson_siegel_spot_yield_formula(1.0, 0.01, 0.01, 0.01, 1.0), expected_yield, rel_tol=1e-6)

def test_nelson_siegel_spot_yield_formula_m_zero():
    # Test behavior at m=0, should return beta0 + beta1 (limit as m->0)
    assert math.isclose(_nelson_siegel_spot_yield_formula(0.0, 0.02, 0.01, 0.03, 1.0), 0.02 + 0.01, rel_tol=1e-9)

def test_nelson_siegel_spot_yield_formula_invalid_tau():
    with pytest.raises(ValueError, match="Tau .* must be positive"):
        _nelson_siegel_spot_yield_formula(1.0, 0.01, 0.01, 0.01, 0.0)
    with pytest.raises(ValueError, match="Tau .* must be positive"):
        _nelson_siegel_spot_yield_formula(1.0, 0.01, 0.01, 0.01, -0.5)

# Test helper function: _nelson_siegel_objective_function
def test_nelson_siegel_objective_function_basic():
    params = np.array([0.04, 0.01, -0.005, 2.0])
    maturities = np.array([1.0, 5.0, 10.0])
    observed_yields = np.array([0.045, 0.042, 0.041])
    
    residuals = _nelson_siegel_objective_function(params, maturities, observed_yields)
    assert isinstance(residuals, np.ndarray)
    assert len(residuals) == len(maturities)
    
    # Check that residuals are non-zero (unless parameters happen to be perfect fit)
    assert not np.all(np.isclose(residuals, 0.0))

def test_nelson_siegel_objective_function_invalid_tau():
    params = np.array([0.04, 0.01, -0.005, -1.0]) # Invalid tau
    maturities = np.array([1.0, 5.0, 10.0])
    observed_yields = np.array([0.045, 0.042, 0.041])
    
    residuals = _nelson_siegel_objective_function(params, maturities, observed_yields)
    assert np.all(np.isinf(residuals)) # Should return infinity for invalid tau


# Test fit_nelson_siegel_curve
def test_fit_nelson_siegel_curve_basic_upward():
    result = fit_nelson_siegel_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD)
    assert isinstance(result, dict)
    assert all(k in result for k in ['beta0', 'beta1', 'beta2', 'tau', 'optim_result'])
    assert result['tau'] > 0 # Tau must be positive
    # Check that optimization was successful
    assert result['optim_result'].success

def test_fit_nelson_siegel_curve_complex_shape():
    result = fit_nelson_siegel_curve(TEST_MATURITIES_COMPLEX, TEST_YIELDS_COMPLEX)
    assert result['optim_result'].success
    assert result['tau'] > 0

def test_fit_nelson_siegel_curve_invalid_inputs():
    with pytest.raises(ValueError, match="Matutities and observed_yields must be NumPy arrays."):
        fit_nelson_siegel_curve([1,2], [0.01, 0.02])
    with pytest.raises(ValueError, match="arrays must have the same shape"):
        fit_nelson_siegel_curve(np.array([1,2]), np.array([0.01]))
    with pytest.raises(ValueError, match="At least 4 data points are required"):
        fit_nelson_siegel_curve(np.array([1,2,3]), np.array([0.01,0.02,0.03]))
    # FIX for the failed test: Ensure enough maturities are provided for this check to be hit first
    with pytest.raises(ValueError, match="Maturities must be positive"):
        fit_nelson_siegel_curve(np.array([-1, 1, 2, 3]), np.array([0.01, 0.02, 0.03, 0.04]))
    with pytest.raises(ValueError, match="Maturities must be sorted"):
        fit_nelson_siegel_curve(np.array([2, 1, 3, 4]), np.array([0.02, 0.01, 0.03, 0.04]))
    with pytest.raises(ValueError, match="Initial parameters for Nelson-Siegel must be a list of 4 values"):
        fit_nelson_siegel_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD, initial_params=[0.01, 0.02])

# Test get_nelson_siegel_spot_yield_curve
def test_get_nelson_siegel_spot_yield_curve_basic():
    fitted_params = {'beta0': 0.04, 'beta1': 0.01, 'beta2': -0.005, 'tau': 2.0}
    maturities_to_eval = np.array([1.0, 5.0, 10.0])
    
    curve = get_nelson_siegel_spot_yield_curve(maturities_to_eval, fitted_params)
    assert isinstance(curve, np.ndarray)
    assert len(curve) == len(maturities_to_eval)
    # Check for reasonable yield values (e.g., positive, not extremely large)
    assert np.all(curve > -0.1) and np.all(curve < 0.2)

def test_get_nelson_siegel_spot_yield_curve_invalid_inputs():
    fitted_params = {'beta0': 0.04, 'beta1': 0.01, 'beta2': -0.005, 'tau': 2.0}
    with pytest.raises(ValueError, match="Maturities to evaluate must be a NumPy array."):
        get_nelson_siegel_spot_yield_curve([1,2], fitted_params)
    with pytest.raises(ValueError, match="Maturities to evaluate must be positive."):
        get_nelson_siegel_spot_yield_curve(np.array([-1, 5]), fitted_params)
    with pytest.raises(ValueError, match="Fitted parameters dictionary is missing"):
        get_nelson_siegel_spot_yield_curve(np.array([1,2]), {'beta0':0.01})
    with pytest.raises(ValueError, match="Error evaluating Nelson-Siegel curve"):
        get_nelson_siegel_spot_yield_curve(np.array([1,2]), {'beta0':0.01, 'beta1':0.01, 'beta2':0.01, 'tau':0.0}) # Invalid tau will cause error

# --- Svensson Model Tests ---

# Test helper function: _svensson_spot_yield_formula
def test_svensson_spot_yield_formula_basic():
    # Example values
    beta0, beta1, beta2, beta3, tau1, tau2 = 0.03, 0.02, 0.01, -0.005, 1.0, 5.0
    m = 2.0
    
    expected_term1 = beta0
    exp_m_tau1 = math.exp(-m / tau1)
    expected_term2 = beta1 * ((1 - exp_m_tau1) / (m / tau1))
    expected_term3 = beta2 * (((1 - exp_m_tau1) / (m / tau1)) - exp_m_tau1)
    exp_m_tau2 = math.exp(-m / tau2)
    expected_term4 = beta3 * (((1 - exp_m_tau2) / (m / tau2)) - exp_m_tau2)
    
    expected_yield = expected_term1 + expected_term2 + expected_term3 + expected_term4
    
    assert math.isclose(_svensson_spot_yield_formula(m, beta0, beta1, beta2, beta3, tau1, tau2), expected_yield, rel_tol=1e-6)

def test_svensson_spot_yield_formula_m_zero():
    # Test behavior at m=0, should return beta0 + beta1 (limit as m->0)
    assert math.isclose(_svensson_spot_yield_formula(0.0, 0.02, 0.01, 0.03, 0.04, 1.0, 5.0), 0.02 + 0.01, rel_tol=1e-9)


def test_svensson_spot_yield_formula_invalid_taus():
    with pytest.raises(ValueError, match="Tau1 and Tau2 .* must be positive"):
        _svensson_spot_yield_formula(1.0, 0.01, 0.01, 0.01, 0.01, 0.0, 1.0)
    with pytest.raises(ValueError, match="Tau1 and Tau2 .* must be positive"):
        _svensson_spot_yield_formula(1.0, 0.01, 0.01, 0.01, 0.01, 1.0, -0.5)


# Test helper function: _svensson_objective_function
def test_svensson_objective_function_basic():
    params = np.array([0.04, 0.01, -0.005, 0.002, 2.0, 5.0])
    maturities = np.array([1.0, 5.0, 10.0])
    observed_yields = np.array([0.045, 0.042, 0.041])
    
    residuals = _svensson_objective_function(params, maturities, observed_yields)
    assert isinstance(residuals, np.ndarray)
    assert len(residuals) == len(maturities)

def test_svensson_objective_function_invalid_taus():
    params = np.array([0.04, 0.01, -0.005, 0.002, -1.0, 5.0]) # Invalid tau1
    maturities = np.array([1.0, 5.0, 10.0])
    observed_yields = np.array([0.045, 0.042, 0.041])
    
    residuals = _svensson_objective_function(params, maturities, observed_yields)
    assert np.all(np.isinf(residuals)) # Should return infinity for invalid tau


# Test fit_svensson_curve
def test_fit_svensson_curve_basic_upward():
    # Svensson typically needs more points than NS
    if len(TEST_MATURITIES) < 6:
        pytest.skip("Test data too small for Svensson model. Need at least 6 points.")
    result = fit_svensson_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD)
    assert isinstance(result, dict)
    assert all(k in result for k in ['beta0', 'beta1', 'beta2', 'beta3', 'tau1', 'tau2', 'optim_result'])
    assert result['tau1'] > 0 and result['tau2'] > 0 # Taus must be positive
    assert result['optim_result'].success

def test_fit_svensson_curve_complex_shape():
    # TEST_MATURITIES_COMPLEX has 8 points, which is >= 6
    if len(TEST_MATURITIES_COMPLEX) < 6:
        pytest.skip("Test data too small for Svensson model. Need at least 6 points.")
    result = fit_svensson_curve(TEST_MATURITIES_COMPLEX, TEST_YIELDS_COMPLEX)
    assert result['optim_result'].success # This is the assertion that failed previously
    assert result['tau1'] > 0 and result['tau2'] > 0

def test_fit_svensson_curve_invalid_inputs():
    with pytest.raises(ValueError, match="Matutities and observed_yields must be NumPy arrays."):
        fit_svensson_curve([1,2,3,4,5,6], [0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
    with pytest.raises(ValueError, match="arrays must have the same shape"):
        fit_svensson_curve(np.array([1,2,3,4,5,6]), np.array([0.01, 0.02, 0.03, 0.04, 0.05]))
    with pytest.raises(ValueError, match="At least 6 data points are required"):
        fit_svensson_curve(np.array([1,2,3,4,5]), np.array([0.01,0.02,0.03,0.04,0.05]))
    # FIX for consistency: Ensure enough maturities are provided for this check to be hit first
    with pytest.raises(ValueError, match="Maturities must be positive"):
        fit_svensson_curve(np.array([-1, 1, 2, 3, 4, 5]), np.array([0.01,0.02,0.03,0.04,0.05, 0.06]))
    with pytest.raises(ValueError, match="Maturities must be sorted"):
        fit_svensson_curve(np.array([2, 1, 3, 4, 5, 6]), np.array([0.02,0.01,0.03,0.04,0.05,0.06]))
    with pytest.raises(ValueError, match="Initial parameters for Svensson must be a list of 6 values"):
        fit_svensson_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD, initial_params=[0.01, 0.02, 0.03, 0.04]) # Wrong number of params

# Test get_svensson_spot_yield_curve
def test_get_svensson_spot_yield_curve_basic():
    fitted_params = {'beta0': 0.04, 'beta1': 0.01, 'beta2': -0.005, 'beta3': 0.002, 'tau1': 2.0, 'tau2': 5.0}
    maturities_to_eval = np.array([1.0, 5.0, 10.0])
    
    curve = get_svensson_spot_yield_curve(maturities_to_eval, fitted_params)
    assert isinstance(curve, np.ndarray)
    assert len(curve) == len(maturities_to_eval)
    assert np.all(curve > -0.1) and np.all(curve < 0.2) # Check for reasonable yield values

def test_get_svensson_spot_yield_curve_invalid_inputs():
    fitted_params = {'beta0': 0.04, 'beta1': 0.01, 'beta2': -0.005, 'beta3': 0.002, 'tau1': 2.0, 'tau2': 5.0}
    with pytest.raises(ValueError, match="Maturities to evaluate must be a NumPy array."):
        get_svensson_spot_yield_curve([1,2], fitted_params)
    with pytest.raises(ValueError, match="Maturities to evaluate must be positive."):
        get_svensson_spot_yield_curve(np.array([-1, 5]), fitted_params)
    with pytest.raises(ValueError, match="Fitted parameters dictionary is missing"):
        get_svensson_spot_yield_curve(np.array([1,2]), {'beta0':0.01})
    with pytest.raises(ValueError, match="Error evaluating Svensson curve"):
        get_svensson_spot_yield_curve(np.array([1,2]), {'beta0':0.01, 'beta1':0.01, 'beta2':0.01, 'beta3':0.01, 'tau1':0.0, 'tau2':1.0}) # Invalid tau will cause error


# --- Cubic Spline Tests ---

# Test fit_cubic_spline_curve
def test_fit_cubic_spline_curve_basic():
    spline_model = fit_cubic_spline_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD)
    assert isinstance(spline_model, CubicSpline)
    # Check that it interpolates the original points (splines by definition pass through knots)
    assert np.allclose(spline_model(TEST_MATURITIES), TEST_YIELDS_UPWARD)

def test_fit_cubic_spline_curve_invalid_inputs():
    with pytest.raises(ValueError, match="Matutities and observed_yields must be NumPy arrays."):
        fit_cubic_spline_curve([1,2], [0.01, 0.02])
    with pytest.raises(ValueError, match="arrays must have the same shape"):
        fit_cubic_spline_curve(np.array([1,2]), np.array([0.01]))
    with pytest.raises(ValueError, match="At least 2 data points are required"):
        fit_cubic_spline_curve(np.array([1]), np.array([0.01]))
    with pytest.raises(ValueError, match="Maturities must be strictly increasing"):
        fit_cubic_spline_curve(np.array([2, 1, 3]), np.array([0.02, 0.01, 0.03]))
    with pytest.raises(ValueError, match="Maturities must be strictly increasing"):
        fit_cubic_spline_curve(np.array([1, 1, 2]), np.array([0.01, 0.01, 0.02])) # Duplicate maturity

# Test get_cubic_spline_spot_yield_curve
def test_get_cubic_spline_spot_yield_curve_basic():
    spline_model = fit_cubic_spline_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD)
    maturities_to_eval = np.array([0.75, 4.0, 12.0, 25.0])
    
    curve = get_cubic_spline_spot_yield_curve(maturities_to_eval, spline_model)
    assert isinstance(curve, np.ndarray)
    assert len(curve) == len(maturities_to_eval)
    # Check for reasonable yield values based on the input range
    assert np.all(curve >= np.min(TEST_YIELDS_UPWARD)) and np.all(curve <= np.max(TEST_YIELDS_UPWARD))

def test_get_cubic_spline_spot_yield_curve_invalid_inputs():
    spline_model = fit_cubic_spline_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD)
    with pytest.raises(ValueError, match="Maturities to evaluate must be a NumPy array."):
        get_cubic_spline_spot_yield_curve([1,2], spline_model)
    with pytest.raises(TypeError, match="spline_model must be a scipy.interpolate.CubicSpline object."):
        get_cubic_spline_spot_yield_curve(np.array([1,2]), "not_a_spline")

# Test curve evaluation outside the fitted range (extrapolation behavior)
def test_spline_extrapolation():
    spline_model = fit_cubic_spline_curve(TEST_MATURITIES, TEST_YIELDS_UPWARD, end_conditions='natural')
    # Test extrapolation for very short and very long maturities
    yield_short = get_cubic_spline_spot_yield_curve(np.array([0.1]), spline_model)
    yield_long = get_cubic_spline_spot_yield_curve(np.array([40.0]), spline_model)
    # Natural splines can behave wildly outside range, so just check it returns a number
    assert isinstance(yield_short, np.ndarray) and len(yield_short) == 1
    assert isinstance(yield_long, np.ndarray) and len(yield_long) == 1
    assert not np.isnan(yield_short[0]) and not np.isinf(yield_short[0])
    assert not np.isnan(yield_long[0]) and not np.isinf(yield_long[0])