# mathematical_functions/credit_risk_advanced.py

import math
from scipy.stats import norm
from scipy.optimize import fsolve # For solving systems of non-linear equations

def _find_implied_asset_values_numerical(E: float, sigma_E: float, D: float, T: float, r: float,
                                         initial_V_guess: float, initial_sigma_V_guess: float) -> tuple[float, float]:
    """
    Numerically solves for the implied asset value (V) and asset volatility (sigma_V)
    given the equity value (E) and equity volatility (sigma_E) using the Merton model equations.

    Args:
        E (float): Firm's Equity Value (Market Capitalization). Must be positive.
        sigma_E (float): Firm's Equity Volatility (annualized, as a decimal). Must be positive.
        D (float): Face Value of Firm's Debt. Must be positive.
        T (float): Time to Debt Maturity (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        initial_V_guess (float): An initial guess for the firm's Asset Value.
        initial_sigma_V_guess (float): An initial guess for the firm's Asset Volatility.

    Returns:
        tuple[float, float]: A tuple containing (implied_asset_value, implied_asset_volatility).

    Raises:
        RuntimeError: If the numerical solver fails to converge or returns non-physical results.
        ValueError: If input parameters are invalid.
    """
    if E <= 0 or sigma_E <= 0 or D <= 0 or T <= 0:
        raise ValueError("Equity value, equity volatility, debt value, and time to maturity must be positive.")

    # Define the system of equations for the solver
    def equations(params):
        V_solver, sigma_V_solver = params

        # Ensure non-negative/non-zero for calculations to avoid math domain errors
        if V_solver <= 0 or sigma_V_solver <= 0:
            # Return large errors to guide solver away from invalid V or sigma_V
            # Using absolute values for large errors to prevent issues with solver direction
            return [1e10, 1e10]

        sigma_V_sqrt_T = sigma_V_solver * math.sqrt(T)
        if sigma_V_sqrt_T <= 1e-9: # Avoid division by zero or extremely small values
            return [1e10, 1e10]

        d1 = (math.log(V_solver / D) + (r + 0.5 * sigma_V_solver**2) * T) / sigma_V_sqrt_T
        d2 = d1 - sigma_V_sqrt_T # Also needed for the first equation's cdf

        # Equation 1: Equity value from BSM formula (residual should be zero)
        # E = V * N(d1) - D * exp(-rT) * N(d2)
        equity_bsm_implied = V_solver * norm.cdf(d1) - D * math.exp(-r * T) * norm.cdf(d2)
        residual1 = equity_bsm_implied - E

        # Equation 2: Equity volatility relationship (residual should be zero)
        # sigma_E * E = V * N(d1) * sigma_V
        # residual2 = (V * N(d1) * sigma_V) - (sigma_E * E)
        residual2 = (V_solver * norm.cdf(d1) * sigma_V_solver) - (sigma_E * E)
        
        return [residual1, residual2]

    try:
        # Initial guess for [V, sigma_V]
        initial_guess = [initial_V_guess, initial_sigma_V_guess]
        
        # Solve the system of non-linear equations
        solution, info, ier, msg = fsolve(equations, initial_guess, full_output=True)
        
        if ier != 1: # ier = 1 indicates successful convergence
            raise RuntimeError(f"Numerical solver failed to converge: {msg}")

        implied_V, implied_sigma_V = solution
        
        # Check for non-physical solutions after convergence
        if implied_V <= 0 or implied_sigma_V <= 0:
            raise RuntimeError("Numerical solver converged to non-physical (non-positive) asset values/volatilities.")
            
        # Verify that the solution is reasonably accurate by re-evaluating residuals
        residual1, residual2 = equations(solution)
        if abs(residual1) > 1e-4 or abs(residual2) > 1e-4: # Check if residuals are close to zero
            raise RuntimeError(f"Numerical solver did not converge accurately. Final residuals: [{residual1:.2e}, {residual2:.2e}]")
            
        return implied_V, implied_sigma_V

    except Exception as e:
        raise RuntimeError(f"An error occurred during numerical solving for Merton model: {e}")


def calculate_merton_model_credit_risk(E: float, sigma_E: float, D: float, T: float, r: float,
                                         initial_V_guess: float = None, initial_sigma_V_guess: float = None) -> dict:
    """
    Calculates key credit risk metrics using the Merton structural model.
    The model treats a firm's equity as a call option on its assets.
    It numerically solves for the implied asset value (V) and asset volatility (sigma_V)
    given observed equity value (E) and equity volatility (sigma_E).

    Args:
        E (float): Firm's Equity Value (Current Market Capitalization). Must be positive.
        sigma_E (float): Firm's Equity Volatility (annualized, as a decimal). Must be positive.
        D (float): Face Value of Firm's Debt (often considered as the strike price). Must be positive.
        T (float): Time to Debt Maturity (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        initial_V_guess (float, optional): An initial guess for the firm's Asset Value.
                                            Defaults to E + D (approximate total value).
        initial_sigma_V_guess (float, optional): An initial guess for the firm's Asset Volatility.
                                                  Defaults to sigma_E.

    Returns:
        dict: A dictionary containing the calculated metrics:
            - 'implied_asset_value': Implied firm asset value (V).
            - 'implied_asset_volatility': Implied firm asset volatility (sigma_V).
            - 'distance_to_default': Number of standard deviations between asset value and default point.
            - 'probability_of_default': Probability that the firm's asset value falls below debt value at maturity.

    Raises:
        ValueError: If any input parameter is invalid (e.g., non-positive where required).
        RuntimeError: If the numerical solver fails to converge or returns non-physical results.

    Assumptions/Limitations:
    - Merton model assumptions hold (Geometric Brownian Motion for assets, single debt maturity).
    - Requires numerical solution, which can be sensitive to initial guesses and convergence.
    - Simplified debt structure (single zero-coupon bond).
    - Equity volatility is assumed to be known and constant.
    """
    if not (E > 0 and sigma_E > 0 and D > 0 and T > 0):
        raise ValueError("Equity value (E), equity volatility (sigma_E), debt value (D), and time to maturity (T) must be positive.")

    # Set default guesses if not provided
    if initial_V_guess is None:
        initial_V_guess = E + D # A common heuristic
    if initial_sigma_V_guess is None:
        initial_sigma_V_guess = sigma_E # Often similar order of magnitude

    try:
        implied_V, implied_sigma_V = _find_implied_asset_values_numerical(E, sigma_E, D, T, r,
                                                                          initial_V_guess, initial_sigma_V_guess)
    except RuntimeError as e:
        raise RuntimeError(f"Failed to find implied asset values for Merton model: {e}")

    # Calculate d1 and d2 using the implied V and sigma_V
    sigma_V_sqrt_T = implied_sigma_V * math.sqrt(T)
    if sigma_V_sqrt_T <= 1e-9: # Handle potential division by zero if sigma_V or T are near zero
        raise RuntimeError("Calculated implied asset volatility or time to maturity is too close to zero, preventing DtD calculation.")

    d1_final = (math.log(implied_V / D) + (r + 0.5 * implied_sigma_V**2) * T) / sigma_V_sqrt_T
    d2_final = d1_final - sigma_V_sqrt_T
    
    # Distance to Default (DtD) and Probability of Default (PD)
    # In Merton model, d2 is typically interpreted as the distance to default in std deviations
    distance_to_default = d2_final 
    probability_of_default = norm.cdf(-distance_to_default) # Risk-neutral PD

    return {
        'implied_asset_value': implied_V,
        'implied_asset_volatility': implied_sigma_V,
        'distance_to_default': distance_to_default,
        'probability_of_default': probability_of_default
    }