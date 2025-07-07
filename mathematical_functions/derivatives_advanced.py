# mathematical_functions/derivatives_advanced.py

import math
import numpy as np
# Import Black-Scholes pricing functions from options_bsm.py
from .options_bsm import black_scholes_call_price, black_scholes_put_price

def binomial_option_price(S: float, K: float, T: float, r: float, sigma: float, n_steps: int, option_type: str = 'call', american: bool = False, q: float = 0) -> float:
    """
    Calculates the price of a European or American option using the Binomial Option Pricing Model.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, continuous compounding, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        n_steps (int): Number of steps in the binomial tree. Must be a positive integer.
        option_type (str, optional): Type of option, 'call' or 'put'. Case-insensitive. Defaults to 'call'.
        american (bool, optional): True for American option, False for European. Defaults to False.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated option price.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive S, K, T, sigma, n_steps).

    Assumptions/Limitations:
    - This is a discrete-time model; result converges to Black-Scholes as n_steps approaches infinity.
    - Risk-free rate and volatility are constant.
    - No transaction costs or taxes.
    - Dividend yield 'q' is continuous.
    - The model simplifies price movements to "up" or "down" steps.
    """
    # Input validation
    if S <= 0:
        raise ValueError("Current stock price (S) must be positive.")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive.")
    if T <= 0:
        raise ValueError("Time to expiration (T) must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility (sigma) must be positive.")
    if not isinstance(n_steps, int) or n_steps <= 0:
        raise ValueError("Number of steps (n_steps) must be a positive integer.")
    if option_type.lower() not in ['call', 'put']:
        raise ValueError("Invalid option_type. Must be 'call' or 'put'.")

    dt = T / n_steps  # Time per step
    u = math.exp(sigma * math.sqrt(dt))  # Up factor
    d = 1 / u  # Down factor
    # Risk-neutral probability (including dividend yield)
    p = (math.exp((r - q) * dt) - d) / (u - d)

    # Calculate stock prices at maturity (last step)
    # stock_prices_at_maturity[j] corresponds to S * u^(n_steps - j) * d^j
    stock_prices_at_maturity = S * (u ** np.arange(n_steps, -1, -1)) * (d ** np.arange(0, n_steps + 1, 1))

    # Initialize option values at maturity (last step)
    option_values = np.zeros(n_steps + 1)

    # Calculate intrinsic values at maturity
    if option_type.lower() == 'call':
        option_values = np.maximum(stock_prices_at_maturity - K, 0)
    else:  # put
        option_values = np.maximum(K - stock_prices_at_maturity, 0)

    # Work backwards through the tree
    for i in range(n_steps - 1, -1, -1): # i represents the current time step (from n-1 down to 0)
        temp_option_values = np.zeros(i + 1)
        
        for j in range(i + 1): # j represents the j-th node at current time step i
            holding_value = (p * option_values[j] + (1 - p) * option_values[j+1]) * math.exp(-r * dt)
            
            current_stock_price = S * (u ** (i - j)) * (d ** j)
            
            if option_type.lower() == 'call':
                intrinsic_value = max(current_stock_price - K, 0)
            else: # put
                intrinsic_value = max(K - current_stock_price, 0)

            if american:
                temp_option_values[j] = max(intrinsic_value, holding_value)
            else:
                temp_option_values[j] = holding_value
        
        option_values = temp_option_values
            
    return option_values[0] # The option price at time 0

def black_scholes_option_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call', q: float = 0) -> float:
    """
    Calculates the price of a European option (call or put) using the Black-Scholes-Merton model.
    This acts as a wrapper around black_scholes_call_price and black_scholes_put_price,
    which are imported from options_bsm.py.

    Args:
        S (float): Current stock price. Must be positive.
        K (float): Option strike price. Must be positive.
        T (float): Time to expiration (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, continuous compounding, as a decimal).
        sigma (float): Volatility of the underlying asset's returns (annualized, as a decimal). Must be positive.
        option_type (str, optional): Type of option, 'call' or 'put'. Case-insensitive. Defaults to 'call'.
        q (float, optional): Continuous dividend yield (annualized, as a decimal). Defaults to 0.

    Returns:
        float: The calculated European option price.

    Raises:
        ValueError: If inputs are invalid or option_type is not 'call' or 'put'.
    """
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        raise ValueError("S, K, T, and sigma must be positive.")
    if option_type.lower() not in ['call', 'put']:
        raise ValueError("Invalid option_type. Must be 'call' or 'put'.")

    if option_type.lower() == 'call':
        return black_scholes_call_price(S, K, T, r, sigma, q)
    else: # 'put'
        return black_scholes_put_price(S, K, T, r, sigma, q)


def calculate_futures_price(spot_price: float, risk_free_rate: float, time_to_maturity: float, dividend_yield_or_cost_of_carry: float = 0) -> float:
    """
    Calculates the theoretical futures price for an asset using continuous compounding.

    Args:
        spot_price (float): The current spot price of the underlying asset. Must be positive.
        risk_free_rate (float): The continuously compounded risk-free interest rate (as a decimal).
        time_to_maturity (float): Time until the futures contract matures (in years). Must be positive.
        dividend_yield_or_cost_of_carry (float, optional): The continuous dividend yield of the underlying asset
                                         (as a decimal) or a general cost of carry (e.g., storage costs).
                                         Defaults to 0.

    Returns:
        float: The theoretical futures price.

    Raises:
        ValueError: If spot_price or time_to_maturity are non-positive.

    Assumptions/Limitations:
    - Assumes continuous compounding for both the risk-free rate and dividend yield/cost of carry.
    - No transaction costs.
    - Market is perfectly efficient.
    """
    if spot_price <= 0:
        raise ValueError("Spot price must be positive.")
    if time_to_maturity <= 0:
        raise ValueError("Time to maturity must be positive.")
    
    # Futures Price = Spot Price * e^((r - q) * T)
    futures_price = spot_price * math.exp((risk_free_rate - dividend_yield_or_cost_of_carry) * time_to_maturity)
    
    return futures_price