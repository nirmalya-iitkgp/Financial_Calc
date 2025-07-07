# mathematical_functions/option_greeks.py

import math
from scipy.stats import norm

def _d1_d2(S: float, K: float, T: float, r: float, sigma: float, q: float) -> tuple[float, float]:
    """
    Helper function to calculate d1 and d2 for the Black-Scholes-Merton model,
    used by the Greeks calculations.

    Args:
        S (float): Current stock price.
        K (float): Option strike price.
        T (float): Time to expiration (in years).
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal).
        q (float): Continuous dividend yield (annualized, as a decimal).

    Returns:
        tuple[float, float]: A tuple containing (d1, d2).

    Raises:
        ValueError: If S, K, sigma, or T are zero or negative, leading to division by zero or invalid calculations.
    """
    if S <= 0:
        raise ValueError("Current stock price (S) must be positive for Greeks calculation.")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive for Greeks calculation.")
    if sigma <= 0:
        raise ValueError("Volatility (sigma) must be positive for Greeks calculation.")
    if T <= 0:
        raise ValueError("Time to expiration (T) must be positive for Greeks calculation.")
        
    sigma_sqrt_T = sigma * math.sqrt(T)

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    
    return d1, d2

def black_scholes_delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call', q: float = 0) -> float:
    """
    Calculates the Delta of a European Option (Call or Put) using the Black-Scholes-Merton model.
    Delta measures the rate of change of the option price with respect to a change in the underlying asset's price.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        option_type (str): Type of option, 'call' or 'put'. Case-insensitive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated Delta value.

    Assumptions/Limitations:
    - Assumes the Black-Scholes-Merton model assumptions hold.
    - S, K, T, sigma must be positive.
    """
    d1, _ = _d1_d2(S, K, T, r, sigma, q)
    
    if option_type.lower() == 'call':
        delta = math.exp(-q * T) * norm.cdf(d1)
    elif option_type.lower() == 'put':
        delta = math.exp(-q * T) * (norm.cdf(d1) - 1)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")
        
    return delta

def black_scholes_gamma(S: float, K: float, T: float, r: float, sigma: float, q: float = 0) -> float:
    """
    Calculates the Gamma of a European Option (same for Call and Put) using the Black-Scholes-Merton model.
    Gamma measures the rate of change of Delta with respect to a change in the underlying asset's price.
    It indicates the convexity of the option's value.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated Gamma value.

    Assumptions/Limitations:
    - Assumes the Black-Scholes-Merton model assumptions hold.
    - S, K, T, sigma must be positive.
    """
    d1, _ = _d1_d2(S, K, T, r, sigma, q)
    
    # Probability density function of standard normal distribution
    N_prime_d1 = norm.pdf(d1)
    
    gamma = math.exp(-q * T) * N_prime_d1 / (S * sigma * math.sqrt(T))
    return gamma

def black_scholes_theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call', q: float = 0) -> float:
    """
    Calculates the Theta of a European Option (Call or Put) using the Black-Scholes-Merton model.
    Theta measures the rate of change of the option price with respect to the passage of time (time decay).
    It is typically negative for long options, meaning option value erodes as time passes.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        option_type (str): Type of option, 'call' or 'put'. Case-insensitive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated Theta value (change per year).

    Assumptions/Limitations:
    - Assumes the Black-Scholes-Merton model assumptions hold.
    - S, K, T, sigma must be positive.
    - The output is "per year". To get "per day", divide by 365.
    """
    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    
    N_prime_d1 = norm.pdf(d1)
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    N_neg_d1 = norm.cdf(-d1)
    N_neg_d2 = norm.cdf(-d2)

    term1 = -(S * math.exp(-q * T) * N_prime_d1 * sigma) / (2 * math.sqrt(T))
    term2_call = q * S * math.exp(-q * T) * N_d1
    term2_put = q * S * math.exp(-q * T) * N_neg_d1
    term3_call = r * K * math.exp(-r * T) * N_d2
    term3_put = r * K * math.exp(-r * T) * N_neg_d2
    
    if option_type.lower() == 'call':
        theta = term1 + term2_call - term3_call
    elif option_type.lower() == 'put':
        theta = term1 - term2_put + term3_put
    else:
        raise ValueError("option_type must be 'call' or 'put'.")
        
    return theta

def black_scholes_vega(S: float, K: float, T: float, r: float, sigma: float, q: float = 0) -> float:
    """
    Calculates the Vega of a European Option (same for Call and Put) using the Black-Scholes-Merton model.
    Vega measures the sensitivity of the option price to changes in the volatility of the underlying asset.
    It indicates how much the option price changes for a 1% change in volatility.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated Vega value.

    Assumptions/Limitations:
    - Assumes the Black-Scholes-Merton model assumptions hold.
    - S, K, T, sigma must be positive.
    - The output is typically interpreted as price change per 1% (0.01) change in sigma.
    """
    d1, _ = _d1_d2(S, K, T, r, sigma, q)
    
    N_prime_d1 = norm.pdf(d1)
    
    vega = S * math.exp(-q * T) * N_prime_d1 * math.sqrt(T)
    return vega

def black_scholes_rho(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call', q: float = 0) -> float:
    """
    Calculates the Rho of a European Option (Call or Put) using the Black-Scholes-Merton model.
    Rho measures the sensitivity of the option price to changes in the risk-free interest rate.
    It indicates how much the option price changes for a 1% change in the risk-free rate.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        option_type (str): Type of option, 'call' or 'put'. Case-insensitive.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated Rho value.

    Assumptions/Limitations:
    - Assumes the Black-Scholes-Merton model assumptions hold.
    - S, K, T, sigma must be positive.
    - The output is typically interpreted as price change per 1% (0.01) change in r.
    """
    _, d2 = _d1_d2(S, K, T, r, sigma, q)
    
    N_d2 = norm.cdf(d2)
    N_neg_d2 = norm.cdf(-d2)
    
    if option_type.lower() == 'call':
        rho = K * T * math.exp(-r * T) * N_d2
    elif option_type.lower() == 'put':
        rho = -K * T * math.exp(-r * T) * N_neg_d2
    else:
        raise ValueError("option_type must be 'call' or 'put'.")
        
    return rho