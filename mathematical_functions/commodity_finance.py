# mathematical_functions/commodity_finance.py

import math
import numpy as np # For numerical operations, especially with correlations

def calculate_commodity_futures_price_cost_of_carry(
    S: float,
    T: float,
    r: float,
    storage_cost_rate: float = 0.0,
    convenience_yield_rate: float = 0.0
) -> float:
    """
    Calculates the theoretical futures price for a commodity based on the cost-of-carry model, incorporating:
    - Current spot price
    - Time to maturity
    - Risk-free interest rate
    - Continuous storage cost rate
    - Continuous convenience yield rate

    The formula used is: F = S * exp((r + u - y) * T)
    where:
    F = Futures Price
    S = Current Spot Price of the commodity
    T = Time to Maturity of the futures contract (in years)
    r = Risk-free interest rate (annualized, continuous compounding)
    u = Continuous storage cost rate (cost of holding the physical commodity, annualized)
    y = Continuous convenience yield rate (benefit of holding the physical commodity, annualized)

    Args:
        S (float): Current spot price of the commodity. Must be positive.
        T (float): Time to maturity of the futures contract (in years). Must be positive.
        r (float): Risk-free interest rate (annualized, as a decimal, continuous compounding).
        storage_cost_rate (float, optional): Continuous storage cost rate (annualized, as a decimal). Defaults to 0.0.
        convenience_yield_rate (float, optional): Continuous convenience yield rate (annualized, as a decimal). Defaults to 0.0.

    Returns:
        float: The calculated theoretical futures price.

    Raises:
        ValueError: If S or T are zero or negative.
    """
    if S <= 0:
        raise ValueError("Current spot price (S) must be positive.")
    if T <= 0:
        raise ValueError("Time to maturity (T) must be positive.")
    
    cost_of_carry_rate = r + storage_cost_rate - convenience_yield_rate
    
    futures_price = S * math.exp(cost_of_carry_rate * T)
    
    return futures_price


def calculate_schwartz_smith_futures_price(
    S: float,
    current_long_term_factor_Z: float, # Renamed for clarity: this is Z_t, the current log-level of the long-term factor
    time_to_maturity: float,
    risk_free_rate: float,
    kappa: float,
    sigma_X: float,
    sigma_Zeta: float,
    rho: float
) -> float:
    """
    Calculates the theoretical futures price using the Schwartz-Smith Two-Factor Model (Model 3).

    This model assumes that the commodity spot price (S) is driven by two unobservable
    stochastic factors:
    1. A short-term factor (X_t) representing short-term deviations from the long-term level.
       It follows an Ornstein-Uhlenbeck process, mean-reverting to zero.
       dX_t = -kappa * X_t * dt + sigma_X * dW_Xt
    2. A long-term factor (Z_t) representing the long-term equilibrium price level (in log units).
       It follows an Arithmetic Brownian Motion (random walk with drift).
       dZ_t = risk_free_rate * dt + sigma_Zeta * dW_Zeta_t (assuming risk_free_rate is the drift under Q)

    The spot price S_t is modeled as S_t = exp(X_t + Z_t). The futures price F(t,T) = E_Q[S_T].

    Args:
        S (float): Current observable spot price of the commodity. Must be positive.
        current_long_term_factor_Z (float): The current value of the long-term factor Z_t.
                                            This should be in LOG UNITS. For example, if the
                                            long-term equilibrium price is $50, this might be log(50).
        time_to_maturity (float): Time to maturity of the futures contract (in years). Must be positive.
        risk_free_rate (float): Risk-free interest rate (annualized, as a decimal, continuous compounding).
                                 This is interpreted as the drift of the Z_t factor under risk-neutral measure.
        kappa (float): The speed of mean reversion for the short-term factor (X_t). Must be positive.
        sigma_X (float): Volatility of the short-term factor (X_t). Must be non-negative.
        sigma_Zeta (float): Volatility of the long-term factor (Z_t). Must be non-negative.
        rho (float): Correlation coefficient between the Wiener processes of X_t and Z_t.
                     Must be between -1 and 1.

    Returns:
        float: The calculated theoretical futures price.

    Raises:
        ValueError: If S, time_to_maturity, kappa are non-positive.
                    If volatilities are negative. If rho is not within [-1, 1].
                    If S and current_long_term_factor_Z are inconsistent (e.g., log(S) - Z_t is too large/small).

    Assumptions/Limitations:
    - Assumes the Schwartz-Smith (1994) two-factor model where S_t = exp(X_t + Z_t).
    - X_t is OU (mean-reverting to 0), Z_t is a Brownian Motion with drift (interpreted as r).
    - Risk-neutral valuation.
    - Parameters (kappa, sigmas, rho, r) are constant.
    - The 'current_long_term_factor_Z' is explicitly the current value of Z_t in log-units.
    """
    if S <= 0:
        raise ValueError("Current spot price (S) must be positive.")
    if time_to_maturity <= 0:
        raise ValueError("Time to maturity must be positive.")
    # current_long_term_factor_Z can be negative or zero as it's a log-level
    if kappa <= 0:
        raise ValueError("Mean reversion rate (kappa) must be positive.")
    if sigma_X < 0 or sigma_Zeta < 0:
        raise ValueError("Volatilities (sigma_X, sigma_Zeta) cannot be negative.")
    if not (-1.0 <= rho <= 1.0):
        raise ValueError("Correlation (rho) must be between -1 and 1.")

    tau = time_to_maturity

    # 1. Infer the current short-term factor (X_t)
    # S_t = exp(X_t + Z_t) => X_t = ln(S_t) - Z_t
    try:
        current_X = math.log(S) - current_long_term_factor_Z
    except ValueError:
        raise ValueError("Cannot compute log(S). S must be positive.")
    except OverflowError:
        raise ValueError("Numerical issue: S or current_long_term_factor_Z may be too large/small for log operations.")


    # 2. Expected value of log spot price at maturity T under risk-neutral measure (E_Q[ln S_T])
    # E_Q[X_T] = X_t * e^(-kappa * tau)
    # E_Q[Z_T] = Z_t + risk_free_rate * tau (assuming risk_free_rate is the drift of Z_t under Q for futures)
    expected_X_T = current_X * math.exp(-kappa * tau)
    expected_Z_T = current_long_term_factor_Z + risk_free_rate * tau

    expected_log_S_T = expected_X_T + expected_Z_T

    # 3. Variance of log spot price at maturity T under risk-neutral measure (Var_Q[ln S_T])
    # Var_Q[X_T] = sigma_X^2 / (2*kappa) * (1 - e^(-2*kappa*tau))
    # Var_Q[Z_T] = sigma_Zeta^2 * tau
    # Cov_Q[X_T, Z_T] = rho * sigma_X * sigma_Zeta / kappa * (1 - e^(-kappa*tau))
    
    # Handle potential division by zero if kappa is extremely small, though input validation prevents kappa <= 0
    if kappa == 0: # Should be caught by input validation, but as a safeguard for edge cases
        var_X_T = sigma_X**2 * tau # Limit as kappa -> 0 for OU process
        cov_X_Z_T = rho * sigma_X * sigma_Zeta * tau # Limit as kappa -> 0
    else:
        var_X_T = (sigma_X**2 / (2 * kappa)) * (1 - math.exp(-2 * kappa * tau))
        cov_X_Z_T = (rho * sigma_X * sigma_Zeta / kappa) * (1 - math.exp(-kappa * tau))

    var_Z_T = sigma_Zeta**2 * tau
    
    total_variance_log_S_T = var_X_T + var_Z_T + 2 * cov_X_Z_T

    # 4. Futures price F(t,T) = E_Q[S_T] = exp(E_Q[ln S_T] + 0.5 * Var_Q[ln S_T])
    log_futures_price = expected_log_S_T + 0.5 * total_variance_log_S_T
    futures_price = math.exp(log_futures_price)

    return futures_price