# mathematical_functions/yield_curve_models.py

import math
import numpy as np
from scipy.optimize import least_squares
from scipy.interpolate import CubicSpline

# --- 1. Nelson-Siegel Model ---

def _nelson_siegel_spot_yield_formula(m: float, beta0: float, beta1: float, beta2: float, tau: float) -> float:
    """
    (HELPER FUNCTION)
    Calculates the Nelson-Siegel spot yield for a given maturity and parameters.

    Args:
        m (float): Maturity (time to maturity, in years).
        beta0 (float): Long-term level parameter.
        beta1 (float): Short-term slope parameter.
        beta2 (float): Medium-term curvature parameter.
        tau (float): Decay parameter (must be positive).

    Returns:
        float: The continuously compounded Nelson-Siegel spot yield.

    Raises:
        ValueError: If tau is non-positive.
    """
    if tau <= 0:
        raise ValueError("Tau (decay parameter) must be positive for Nelson-Siegel model.")

    term1 = beta0
    term2 = beta1 * ((1 - math.exp(-m / tau)) / (m / tau)) if m != 0 else beta1 # Handle m=0 for limits
    term3 = beta2 * (((1 - math.exp(-m / tau)) / (m / tau)) - math.exp(-m / tau)) if m != 0 else 0.0 # Handle m=0 for limits

    return term1 + term2 + term3

def _nelson_siegel_objective_function(params: np.ndarray, maturities: np.ndarray, observed_yields: np.ndarray) -> np.ndarray:
    """
    (HELPER FUNCTION)
    Objective function for Nelson-Siegel model fitting (minimizes sum of squared errors).

    Args:
        params (np.ndarray): Array of Nelson-Siegel parameters [beta0, beta1, beta2, tau].
        maturities (np.ndarray): Array of observed maturities.
        observed_yields (np.ndarray): Array of observed yields corresponding to maturities.

    Returns:
        np.ndarray: Array of residuals (observed_yield - model_yield).
    """
    beta0, beta1, beta2, tau = params
    
    # Ensure tau is positive during optimization
    if tau <= 0:
        # Penalize negative or zero tau heavily to guide optimization
        return np.full_like(observed_yields, np.inf)

    model_yields = np.array([_nelson_siegel_spot_yield_formula(m, beta0, beta1, beta2, tau) for m in maturities])
    return observed_yields - model_yields


def fit_nelson_siegel_curve(maturities: np.ndarray, observed_yields: np.ndarray, initial_params: list = None) -> dict:
    """
    Fits the Nelson-Siegel model to observed market yields.

    Args:
        maturities (np.ndarray): A 1D NumPy array of maturities (in years) corresponding to observed_yields.
                                 Must be positive and sorted.
        observed_yields (np.ndarray): A 1D NumPy array of observed yields (as decimals) corresponding to maturities.
        initial_params (list, optional): Initial guess for the parameters [beta0, beta1, beta2, tau].
                                         If None, a default guess is used.

    Returns:
        dict: A dictionary containing the fitted parameters ('beta0', 'beta1', 'beta2', 'tau')
              and the optimization result ('optim_result').

    Raises:
        ValueError: If inputs are invalid or fitting fails.
    """
    if not isinstance(maturities, np.ndarray) or not isinstance(observed_yields, np.ndarray):
        raise ValueError("Matutities and observed_yields must be NumPy arrays.")
    if maturities.shape != observed_yields.shape:
        raise ValueError("Matutities and observed_yields arrays must have the same shape.")
    if len(maturities) < 4: # Need at least 4 points to fit 4 parameters reasonably
        raise ValueError("At least 4 data points are required to fit the Nelson-Siegel model.")
    if np.any(maturities <= 0):
        raise ValueError("Maturities must be positive.")
    if not np.all(np.diff(maturities) > 0):
        raise ValueError("Maturities must be sorted in ascending order.")

    if initial_params is None:
        # A reasonable default initial guess
        # beta0: long-term yield (e.g., longest observed)
        # beta1: difference between short-term and long-term yield (slope)
        # beta2: curvature, often small initially
        # tau: decay, typically around 1-5 years
        _beta0_init = observed_yields[-1] if len(observed_yields) > 0 else 0.05
        _beta1_init = observed_yields[0] - _beta0_init if len(observed_yields) > 0 else 0.0
        _beta2_init = 0.0
        _tau_init = 1.0 # Common initial guess for tau
        initial_params = [_beta0_init, _beta1_init, _beta2_init, _tau_init]
    
    if len(initial_params) != 4:
        raise ValueError("Initial parameters for Nelson-Siegel must be a list of 4 values.")

    # Bounds for parameters during optimization (optional but can help convergence)
    # beta0, beta1, beta2 can be positive or negative
    # tau must be positive
    bounds = ([-np.inf, -np.inf, -np.inf, 1e-6], [np.inf, np.inf, np.inf, np.inf])

    try:
        # Use least_squares for non-linear optimization
        result = least_squares(
            _nelson_siegel_objective_function,
            initial_params,
            args=(maturities, observed_yields),
            bounds=bounds,
            loss='linear',  # Use linear loss for standard least squares
            jac='3-point' # Numerical Jacobian estimation
        )
        
        if not result.success:
            raise RuntimeError(f"Nelson-Siegel fitting failed: {result.message}")

        beta0, beta1, beta2, tau = result.x
        return {
            'beta0': beta0,
            'beta1': beta1,
            'beta2': beta2,
            'tau': tau,
            'optim_result': result
        }
    except Exception as e:
        raise RuntimeError(f"An error occurred during Nelson-Siegel fitting: {e}")

def get_nelson_siegel_spot_yield_curve(maturities_to_evaluate: np.ndarray, fitted_params: dict) -> np.ndarray:
    """
    Generates the Nelson-Siegel spot yield curve for specified maturities using fitted parameters.

    Args:
        maturities_to_evaluate (np.ndarray): A 1D NumPy array of maturities (in years) at which to calculate the yield.
        fitted_params (dict): A dictionary containing the fitted Nelson-Siegel parameters
                              ('beta0', 'beta1', 'beta2', 'tau').

    Returns:
        np.ndarray: A 1D NumPy array of continuously compounded spot yields corresponding to maturities_to_evaluate.

    Raises:
        ValueError: If inputs are invalid or parameters are missing.
    """
    if not isinstance(maturities_to_evaluate, np.ndarray):
        raise ValueError("Maturities to evaluate must be a NumPy array.")
    if np.any(maturities_to_evaluate <= 0):
        raise ValueError("Maturities to evaluate must be positive.")
    if not all(k in fitted_params for k in ['beta0', 'beta1', 'beta2', 'tau']):
        raise ValueError("Fitted parameters dictionary is missing required keys for Nelson-Siegel model.")

    beta0 = fitted_params['beta0']
    beta1 = fitted_params['beta1']
    beta2 = fitted_params['beta2']
    tau = fitted_params['tau']

    try:
        yield_curve = np.array([_nelson_siegel_spot_yield_formula(m, beta0, beta1, beta2, tau) for m in maturities_to_evaluate])
        return yield_curve
    except ValueError as e:
        raise ValueError(f"Error evaluating Nelson-Siegel curve: {e}")

# --- 2. Svensson Model ---

def _svensson_spot_yield_formula(m: float, beta0: float, beta1: float, beta2: float, beta3: float, tau1: float, tau2: float) -> float:
    """
    (HELPER FUNCTION)
    Calculates the Svensson spot yield for a given maturity and parameters.

    Args:
        m (float): Maturity (time to maturity, in years).
        beta0 (float): Long-term level parameter.
        beta1 (float): Short-term slope parameter.
        beta2 (float): First curvature parameter.
        beta3 (float): Second curvature parameter.
        tau1 (float): First decay parameter (must be positive).
        tau2 (float): Second decay parameter (must be positive).

    Returns:
        float: The continuously compounded Svensson spot yield.

    Raises:
        ValueError: If tau1 or tau2 are non-positive.
    """
    if tau1 <= 0 or tau2 <= 0:
        raise ValueError("Tau1 and Tau2 (decay parameters) must be positive for Svensson model.")

    term1 = beta0
    
    # Handle m=0 for limit calculations
    if m == 0:
        term2 = beta1
        term3 = 0.0
        term4 = 0.0
    else:
        exp_m_tau1 = math.exp(-m / tau1)
        term2 = beta1 * ((1 - exp_m_tau1) / (m / tau1))
        term3 = beta2 * (((1 - exp_m_tau1) / (m / tau1)) - exp_m_tau1)
        
        exp_m_tau2 = math.exp(-m / tau2)
        term4 = beta3 * (((1 - exp_m_tau2) / (m / tau2)) - exp_m_tau2)

    return term1 + term2 + term3 + term4

def _svensson_objective_function(params: np.ndarray, maturities: np.ndarray, observed_yields: np.ndarray) -> np.ndarray:
    """
    (HELPER FUNCTION)
    Objective function for Svensson model fitting (minimizes sum of squared errors).

    Args:
        params (np.ndarray): Array of Svensson parameters [beta0, beta1, beta2, beta3, tau1, tau2].
        maturities (np.ndarray): Array of observed maturities.
        observed_yields (np.ndarray): Array of observed yields corresponding to maturities.

    Returns:
        np.ndarray: Array of residuals (observed_yield - model_yield).
    """
    beta0, beta1, beta2, beta3, tau1, tau2 = params

    # Ensure tau parameters are positive during optimization
    if tau1 <= 0 or tau2 <= 0:
        return np.full_like(observed_yields, np.inf)

    model_yields = np.array([_svensson_spot_yield_formula(m, beta0, beta1, beta2, beta3, tau1, tau2) for m in maturities])
    return observed_yields - model_yields


def fit_svensson_curve(maturities: np.ndarray, observed_yields: np.ndarray, initial_params: list = None) -> dict:
    """
    Fits the Svensson model to observed market yields.

    Args:
        maturities (np.ndarray): A 1D NumPy array of maturities (in years) corresponding to observed_yields.
                                 Must be positive and sorted.
        observed_yields (np.ndarray): A 1D NumPy array of observed yields (as decimals) corresponding to maturities.
        initial_params (list, optional): Initial guess for the parameters [beta0, beta1, beta2, beta3, tau1, tau2].
                                         If None, a default guess is used.

    Returns:
        dict: A dictionary containing the fitted parameters ('beta0', 'beta1', 'beta2', 'beta3', 'tau1', 'tau2')
              and the optimization result ('optim_result').

    Raises:
        ValueError: If inputs are invalid or fitting fails.
    """
    if not isinstance(maturities, np.ndarray) or not isinstance(observed_yields, np.ndarray):
        raise ValueError("Matutities and observed_yields must be NumPy arrays.")
    if maturities.shape != observed_yields.shape:
        raise ValueError("Matutities and observed_yields arrays must have the same shape.")
    if len(maturities) < 6: # Need at least 6 points to fit 6 parameters reasonably
        raise ValueError("At least 6 data points are required to fit the Svensson model.")
    if np.any(maturities <= 0):
        raise ValueError("Maturities must be positive.")
    if not np.all(np.diff(maturities) > 0):
        raise ValueError("Maturities must be sorted in ascending order.")

    if initial_params is None:
        # Default guess often starts from Nelson-Siegel like values
        _beta0_init = observed_yields[-1] if len(observed_yields) > 0 else 0.05
        _beta1_init = observed_yields[0] - _beta0_init if len(observed_yields) > 0 else 0.0
        _beta2_init = 0.0
        _beta3_init = 0.0 # New parameter often initialized to zero
        _tau1_init = 1.0
        _tau2_init = 5.0 # A common practice is to have tau2 >> tau1
        initial_params = [_beta0_init, _beta1_init, _beta2_init, _beta3_init, _tau1_init, _tau2_init]
    
    if len(initial_params) != 6:
        raise ValueError("Initial parameters for Svensson must be a list of 6 values.")

    bounds = ([-np.inf, -np.inf, -np.inf, -np.inf, 1e-6, 1e-6], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])

    try:
        result = least_squares(
            _svensson_objective_function,
            initial_params,
            args=(maturities, observed_yields),
            bounds=bounds,
            loss='linear',
            jac='3-point',
            # --- START OF CHANGES ---
            max_nfev=3000, # Increased from 2000 (or default 600)
            ftol=1e-7      # Relaxed the tolerance on the change in cost function from default 1e-8
            # --- END OF CHANGES ---
        )

        if not result.success:
            raise RuntimeError(f"Svensson fitting failed: {result.message}. Status: {result.status}. Optimal point: {result.x if result.x is not None else 'N/A'}. Cost: {result.cost}. Number of function evaluations: {result.nfev}.")

        beta0, beta1, beta2, beta3, tau1, tau2 = result.x
        return {
            'beta0': beta0,
            'beta1': beta1,
            'beta2': beta2,
            'beta3': beta3,
            'tau1': tau1,
            'tau2': tau2,
            'optim_result': result
        }
    except Exception as e:
        # Catch any other unexpected errors during the optimization process
        raise RuntimeError(f"An error occurred during Svensson fitting: {e}")


def get_svensson_spot_yield_curve(maturities_to_evaluate: np.ndarray, fitted_params: dict) -> np.ndarray:
    """
    Generates the Svensson spot yield curve for specified maturities using fitted parameters.

    Args:
        maturities_to_evaluate (np.ndarray): A 1D NumPy array of maturities (in years) at which to calculate the yield.
        fitted_params (dict): A dictionary containing the fitted Svensson parameters
                              ('beta0', 'beta1', 'beta2', 'beta3', 'tau1', 'tau2').

    Returns:
        np.ndarray: A 1D NumPy array of continuously compounded spot yields corresponding to maturities_to_evaluate.

    Raises:
        ValueError: If inputs are invalid or parameters are missing.
    """
    if not isinstance(maturities_to_evaluate, np.ndarray):
        raise ValueError("Maturities to evaluate must be a NumPy array.")
    if np.any(maturities_to_evaluate <= 0):
        raise ValueError("Maturities to evaluate must be positive.")
    if not all(k in fitted_params for k in ['beta0', 'beta1', 'beta2', 'beta3', 'tau1', 'tau2']):
        raise ValueError("Fitted parameters dictionary is missing required keys for Svensson model.")

    beta0 = fitted_params['beta0']
    beta1 = fitted_params['beta1']
    beta2 = fitted_params['beta2']
    beta3 = fitted_params['beta3']
    tau1 = fitted_params['tau1']
    tau2 = fitted_params['tau2']

    try:
        yield_curve = np.array([_svensson_spot_yield_formula(m, beta0, beta1, beta2, beta3, tau1, tau2) for m in maturities_to_evaluate])
        return yield_curve
    except ValueError as e:
        raise ValueError(f"Error evaluating Svensson curve: {e}")


# --- 3. Spline Functions (Cubic Spline) ---
# We will leverage scipy's CubicSpline which handles the complex
# piecewise polynomial calculation and coefficient determination internally.

def fit_cubic_spline_curve(maturities: np.ndarray, observed_yields: np.ndarray, end_conditions: str = 'natural') -> CubicSpline:
    """
    Fits a cubic spline to observed market yields.

    Args:
        maturities (np.ndarray): A 1D NumPy array of maturities (in years) corresponding to observed_yields.
                                 Must be strictly increasing.
        observed_yields (np.ndarray): A 1D NumPy array of observed yields (as decimals) corresponding to maturities.
        end_conditions (str): Boundary condition for the spline.
                              'natural' (default): second derivatives at endpoints are zero.
                              'not-a-knot': first and second segments on each end are the same polynomial.
                              See scipy.interpolate.CubicSpline documentation for more options.

    Returns:
        scipy.interpolate.CubicSpline: A CubicSpline object that can be called like a function to
                                       get yields for any maturity.

    Raises:
        ValueError: If inputs are invalid.
    """
    if not isinstance(maturities, np.ndarray) or not isinstance(observed_yields, np.ndarray):
        raise ValueError("Matutities and observed_yields must be NumPy arrays.")
    if maturities.shape != observed_yields.shape:
        raise ValueError("Matutities and observed_yields arrays must have the same shape.")
    if len(maturities) < 2:
        raise ValueError("At least 2 data points are required to fit a spline.")
    if not np.all(np.diff(maturities) > 0):
        raise ValueError("Maturities must be strictly increasing.")
    
    # Note: Scipy's CubicSpline handles the coefficient determination based on the provided
    # maturities (knots) and observed_yields. The internal representation will be the
    # piecewise polynomial segments.

    try:
        # The CubicSpline object itself is the "fitted model"
        spline_model = CubicSpline(maturities, observed_yields, bc_type=end_conditions)
        return spline_model
    except Exception as e:
        raise RuntimeError(f"An error occurred during cubic spline fitting: {e}")

def get_cubic_spline_spot_yield_curve(maturities_to_evaluate: np.ndarray, spline_model: CubicSpline) -> np.ndarray:
    """
    Generates the cubic spline spot yield curve for specified maturities using a fitted spline model.

    Args:
        maturities_to_evaluate (np.ndarray): A 1D NumPy array of maturities (in years) at which to calculate the yield.
        spline_model (scipy.interpolate.CubicSpline): A fitted CubicSpline object returned by fit_cubic_spline_curve.

    Returns:
        np.ndarray: A 1D NumPy array of continuously compounded spot yields corresponding to maturities_to_evaluate.

    Raises:
        ValueError: If inputs are invalid.
        TypeError: If spline_model is not a CubicSpline object.
    """
    if not isinstance(maturities_to_evaluate, np.ndarray):
        raise ValueError("Maturities to evaluate must be a NumPy array.")
    if not isinstance(spline_model, CubicSpline):
        raise TypeError("spline_model must be a scipy.interpolate.CubicSpline object.")
    
    try:
        # The CubicSpline object is callable to evaluate the curve
        yield_curve = spline_model(maturities_to_evaluate)
        return yield_curve
    except Exception as e:
        raise ValueError(f"Error evaluating cubic spline curve: {e}")