# mathematical_functions/options_bsm.py

import math
from scipy.stats import norm

def _d1_d2(S: float, K: float, T: float, r: float, sigma: float, q: float = 0) -> tuple[float, float]:
    """
    Helper function to calculate d1 and d2 for the Black-Scholes-Merton model.

    Args:
        S (float): Current stock price.
        K (float): Option strike price.
        T (float): Time to expiration (in years).
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal).
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        tuple[float, float]: A tuple containing (d1, d2).

    Raises:
        ValueError: If S, K, sigma, or T are zero or negative, leading to division by zero or invalid calculations.
    """
    if S <= 0:
        raise ValueError("Current stock price (S) must be positive for d1/d2 calculation.")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive for d1/d2 calculation.")
    if sigma <= 0:
        raise ValueError("Volatility (sigma) must be positive.")
    if T <= 0:
        raise ValueError("Time to expiration (T) must be positive.")
    
    sigma_sqrt_T = sigma * math.sqrt(T)

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    
    return d1, d2

def black_scholes_call_price(S: float, K: float, T: float, r: float, sigma: float, q: float = 0) -> float:
    """
    Calculates the price of a European Call Option using the Black-Scholes-Merton model.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated European Call Option price.

    Assumptions/Limitations:
    - European-style option (can only be exercised at expiration).
    - No dividends (unless q is specified).
    - Lognormal distribution of asset prices.
    - Constant risk-free rate, volatility, and dividend yield.
    - No transaction costs or taxes.
    - Can only be applied if T > 0 and sigma > 0.
    """
    # These checks are now also present in _d1_d2, but keeping them here for clarity
    # for direct calls to this function, and for potentially different error messages.
    if S <= 0:
        raise ValueError("Current stock price (S) must be positive.")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive.")
    # T and sigma handled in _d1_d2 helper
    
    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    
    # Cumulative distribution function of standard normal distribution
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    
    call_price = S * math.exp(-q * T) * N_d1 - K * math.exp(-r * T) * N_d2
    return call_price

def black_scholes_put_price(S: float, K: float, T: float, r: float, sigma: float, q: float = 0) -> float:
    """
    Calculates the price of a European Put Option using the Black-Scholes-Merton model.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated European Put Option price.

    Assumptions/Limitations:
    - European-style option.
    - No dividends (unless q is specified).
    - Lognormal distribution of asset prices.
    - Constant risk-free rate, volatility, and dividend yield.
    - No transaction costs or taxes.
    - Can only be applied if T > 0 and sigma > 0.
    """
    # These checks are now also present in _d1_d2, but keeping them here for clarity
    # for direct calls to this function, and for potentially different error messages.
    if S <= 0:
        raise ValueError("Current stock price (S) must be positive.")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive.")
    # T and sigma handled in _d1_d2 helper

    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    
    # Cumulative distribution function of standard normal distribution
    N_neg_d1 = norm.cdf(-d1)
    N_neg_d2 = norm.cdf(-d2)
    
    put_price = K * math.exp(-r * T) * N_neg_d2 - S * math.exp(-q * T) * N_neg_d1
    return put_price