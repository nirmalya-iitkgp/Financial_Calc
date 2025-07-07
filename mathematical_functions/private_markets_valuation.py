# mathematical_functions/private_markets_valuation.py

import math
import numpy as np
from scipy.stats import norm # For option pricing components

def calculate_illiquidity_discount_option_model(
    asset_value: float,
    liquidation_cost_pct: float, # Percentage of asset value lost if liquidated immediately
    holding_period: float,       # Time (in years) the asset is expected to be held before potential sale
    volatility: float,           # Annualized volatility of the asset's value
    risk_free_rate: float,       # Annualized risk-free interest rate (continuous compounding)
    g_spread: float = 0.0        # Spread to risk-free rate reflecting specific asset/illiquidity risk premium
) -> dict:
    """
    Calculates an illiquidity discount using an option-pricing analogy,
    inspired by models like Longstaff (1999) and others who frame illiquidity
    as the cost of not being able to sell immediately.

    This model frames the illiquidity as a put option on the asset, where the
    exercise price is the asset's value less immediate liquidation costs, and
    the option protects against further value decline during the holding period.

    A simplified interpretation is that the illiquidity cost is similar to
    the value of a European put option with strike price = (1 - liquidation_cost_pct) * asset_value,
    and the underlying is the asset value itself, expiring at the end of the holding period.
    The holder pays a premium (the illiquidity discount) to avoid the immediate liquidation cost
    and realize a potentially higher value later.

    Args:
        asset_value (float): Current market value of the illiquid asset. Must be positive.
        liquidation_cost_pct (float): Percentage cost incurred if the asset were to be
                                      liquidated immediately (e.g., 0.10 for 10% cost). Must be >= 0.
        holding_period (float): Expected time (in years) the asset will be held before it
                                can be potentially sold. Must be positive.
        volatility (float): Annualized volatility of the asset's value. Must be positive.
        risk_free_rate (float): Annualized risk-free interest rate (as a decimal, continuous compounding).
        g_spread (float, optional): An additional spread added to the risk-free rate to reflect
                                    the specific illiquidity risk. Defaults to 0.0. This can capture
                                    additional required return for illiquidity.

    Returns:
        dict: A dictionary containing:
              - 'illiquidity_discount_value': The calculated value of the illiquidity discount.
              - 'illiquidity_discount_pct': The discount as a percentage of the asset value.
              - 'adjusted_asset_value': Asset value after applying the discount.

    Raises:
        ValueError: If input parameters are invalid (e.g., non-positive, out of range).

    Note: This is a simplified option-based model. More sophisticated models exist,
          but this provides a strong academic foundation.
    """
    if asset_value <= 0:
        raise ValueError("Asset value must be positive.")
    if not (0 <= liquidation_cost_pct < 1): # Cost should be less than 100%
        raise ValueError("Liquidation cost percentage must be between 0 and 1 (exclusive of 1).")
    if holding_period <= 0:
        raise ValueError("Holding period must be positive.")
    if volatility <= 0:
        raise ValueError("Volatility must be positive.")
    if g_spread < 0:
        raise ValueError("G-spread cannot be negative.")

    # The effective 'strike price' (K) is the value obtained from immediate liquidation
    K_immediate_liquidation = asset_value * (1 - liquidation_cost_pct)
    
    # We model the illiquidity discount as a put option that allows avoiding the immediate loss
    # and instead selling at a future expected value, but with inherent risk.
    # The effective risk-free rate for discounting here could incorporate the g_spread.
    r_eff = risk_free_rate + g_spread

    # Using Black-Scholes-Merton for a European put option:
    # S = asset_value (current asset value)
    # K = K_immediate_liquidation (the "salvage value" or alternative if not held)
    # T = holding_period
    # r = r_eff
    # sigma = volatility
    # q = 0 (assuming no continuous dividends/cash flows from the illiquid asset for this specific model)

    d1 = (math.log(asset_value / K_immediate_liquidation) + (r_eff + 0.5 * volatility**2) * holding_period) / \
         (volatility * math.sqrt(holding_period))
    d2 = d1 - volatility * math.sqrt(holding_period)

    # The value of the "option to avoid immediate liquidation loss"
    # This value represents the additional "cost" or "discount" of illiquidity.
    illiquidity_option_value = K_immediate_liquidation * math.exp(-r_eff * holding_period) * norm.cdf(-d2) - \
                               asset_value * norm.cdf(-d1)

    # The illiquidity discount is the value of this put option.
    illiquidity_discount_value = illiquidity_option_value
    
    # The final illiquidity discount is usually thought of as the sum of the direct liquidation cost
    # PLUS the option value representing the cost of holding it through uncertainty to avoid that cost.
    # A common interpretation in academia is that the illiquidity discount is the value of holding a security that *cannot* be sold.
    # Its value is how much less one would pay for the illiquid asset compared to an identical liquid one.
    # An alternative framing for the discount is the difference between the liquid value and the illiquid value.
    # Longstaff (1995, J. Finance) defines illiquidity discount as the value of the option to delay sale.
    # This implies the asset value `S` is the liquid value, and the `illiquidity_option_value` is the discount.

    illiquidity_discount_pct = illiquidity_discount_value / asset_value if asset_value > 0 else 0
    adjusted_asset_value = asset_value - illiquidity_discount_value

    return {
        'illiquidity_discount_value': illiquidity_discount_value,
        'illiquidity_discount_pct': illiquidity_discount_pct,
        'adjusted_asset_value': adjusted_asset_value
    }


def calculate_real_estate_terminal_value_gordon_growth(
    net_operating_income_next_period: float,
    exit_cap_rate: float,
    long_term_growth_rate: float
) -> float:
    """
    Calculates the terminal value (exit value) of a real estate property
    using the Gordon Growth Model (GGM) approach, often used in DCF for real estate.

    Terminal Value = NOI_next_period / (Exit_Cap_Rate - Long_Term_Growth_Rate)

    Args:
        net_operating_income_next_period (float): The projected Net Operating Income (NOI)
                                                 for the period immediately following the
                                                 explicit forecast period (NOI_n+1). Must be positive.
        exit_cap_rate (float): The capitalization rate (as a decimal) at which the property
                               is expected to be sold at the end of the holding period. Must be positive.
        long_term_growth_rate (float): The assumed constant long-term growth rate (as a decimal)
                                       of NOI beyond the forecast period. Must be less than `exit_cap_rate`.

    Returns:
        float: The calculated terminal value of the real estate property.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive NOI/cap rate, growth rate >= cap rate).
    """
    if net_operating_income_next_period <= 0:
        raise ValueError("Net Operating Income (NOI) for the next period must be positive.")
    if exit_cap_rate <= 0:
        raise ValueError("Exit capitalization rate must be positive.")
    if long_term_growth_rate >= exit_cap_rate:
        raise ValueError("Long-term growth rate must be less than the exit capitalization rate.")

    terminal_value = net_operating_income_next_period / (exit_cap_rate - long_term_growth_rate)
    return terminal_value


def simulate_private_equity_valuation_monte_carlo(
    base_free_cash_flows: list,  # List of FCFs for explicit forecast period
    terminal_value_growth_rate_mean: float,
    terminal_value_growth_rate_std: float,
    discount_rate_mean: float,
    discount_rate_std: float,
    exit_multiple_mean: float,
    exit_multiple_std: float,
    num_simulations: int,
    exit_year: int,              # Year in the forecast when exit occurs (index-based or actual year)
    seed: int = None
) -> dict:
    """
    Performs a Monte Carlo simulation for a private equity valuation (e.g., DCF-based).
    It simulates key uncertain inputs (terminal value growth, discount rate, exit multiple)
    to generate a distribution of NPVs/Valuations.

    Args:
        base_free_cash_flows (list): A list of deterministic Free Cash Flows (FCF)
                                     for the explicit forecast period. E.g., [FCF_Y1, FCF_Y2, ..., FCF_Yn].
                                     Assumes FCFs are at year-end.
        terminal_value_growth_rate_mean (float): Mean of the normal distribution for long-term growth rate
                                                 used in terminal value calculation.
        terminal_value_growth_rate_std (float): Standard deviation of the normal distribution for
                                                long-term growth rate.
        discount_rate_mean (float): Mean of the normal distribution for the discount rate (WACC).
        discount_rate_std (float): Standard deviation of the normal distribution for the discount rate.
        exit_multiple_mean (float): Mean of the normal distribution for the exit multiple (e.g., EV/EBITDA).
        exit_multiple_std (float): Standard deviation of the normal distribution for the exit multiple.
        num_simulations (int): Number of Monte Carlo simulation runs. Must be positive.
        exit_year (int): The year (index, starting from 1) at which the exit occurs.
                         Must be within the range of `base_free_cash_flows` length + 1.
                         E.g., if FCFs are for 5 years, exit_year could be 5 or 6 (for terminal value).
        seed (int, optional): Seed for random number generation for reproducibility. Defaults to None.

    Returns:
        dict: A dictionary containing simulation results:
              - 'simulated_valuations': A numpy array of all simulated valuations.
              - 'mean_valuation': Mean of the simulated valuations.
              - 'median_valuation': Median of the simulated valuations.
              - 'valuation_percentiles': A dictionary with 5th, 25th, 75th, 95th percentiles.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive simulations, invalid exit_year).
    """
    if not isinstance(base_free_cash_flows, list) or not all(isinstance(fcf, (int, float)) for fcf in base_free_cash_flows):
        raise ValueError("base_free_cash_flows must be a list of numbers.")
    if num_simulations <= 0 or not isinstance(num_simulations, int):
        raise ValueError("Number of simulations must be a positive integer.")
    if not (1 <= exit_year <= len(base_free_cash_flows) + 1):
        raise ValueError("Exit year must be a positive integer within the plausible range of forecast period.")
    if any(std < 0 for std in [terminal_value_growth_rate_std, discount_rate_std, exit_multiple_std]):
        raise ValueError("Standard deviations cannot be negative.")
    if seed is not None and not isinstance(seed, int):
        raise ValueError("Seed must be an integer or None.")
        
    np.random.seed(seed) # This line will now be safe
    np.random.seed(seed)

    simulated_valuations = np.zeros(num_simulations)
    num_forecast_years = len(base_free_cash_flows)

    for i in range(num_simulations):
        # Sample parameters from normal distributions (can use other dists as well)
        # Ensure parameters remain reasonable (e.g., non-negative discount rate)
        growth_rate = max(0.0, np.random.normal(terminal_value_growth_rate_mean, terminal_value_growth_rate_std))
        discount_rate = max(0.01, np.random.normal(discount_rate_mean, discount_rate_std)) # Min discount rate
        exit_multiple = max(0.0, np.random.normal(exit_multiple_mean, exit_multiple_std))

        # Calculate present value of explicit cash flows
        pv_explicit_fcf = 0.0
        for year in range(num_forecast_years):
            pv_explicit_fcf += base_free_cash_flows[year] / ((1 + discount_rate)**(year + 1))
        
        # Calculate terminal value
        terminal_value = 0.0
        if exit_year <= num_forecast_years: # Exit at end of forecast period
            # Use Gordon Growth Model for terminal value
            if base_free_cash_flows[exit_year - 1] <= 0: # Check for non-positive FCF before GGM
                # If last FCF is non-positive, GGM is problematic. Use exit multiple if possible.
                # For simplicity, if FCF is non-positive, treat TV as 0 or handle separately.
                terminal_value_fcf = 0.0
            else:
                terminal_value_fcf = base_free_cash_flows[exit_year - 1] * (1 + growth_rate) / (discount_rate - growth_rate)

            # Use exit multiple method for terminal value as an alternative or primary
            # This assumes a multiple of a relevant metric (e.g., EBITDA) in the exit year.
            # Here, for simplicity, we'll assume FCF is a proxy for the metric and apply multiple.
            # In a real LBO, this would be based on projected EBITDA, revenue etc.
            # We'll use the last FCF as the basis for the multiple if it's there.
            if len(base_free_cash_flows) >= exit_year:
                 terminal_value_multiple = base_free_cash_flows[exit_year - 1] * exit_multiple
            else:
                terminal_value_multiple = 0.0 # Should not happen if exit_year <= num_forecast_years

            # A simplistic way to combine, but in practice, one method is typically used
            # Let's prioritize the exit multiple as it's common in PE.
            terminal_value = terminal_value_multiple 
            
            # If (discount_rate - growth_rate) is problematic, ensure TV is handled.
            if discount_rate <= growth_rate: # Handle case where GGM denominator is non-positive
                # This makes GGM explode; cap TV or set to a very high value indicating problem.
                # In practice, this simulation would need to ensure growth_rate < discount_rate
                # or use a different TV methodology (e.g., fixed terminal multiple).
                # For this function, let's just default to exit multiple if GGM is invalid.
                pass # Already using terminal_value_multiple as primary

        elif exit_year == num_forecast_years + 1: # Exit in the first year after explicit forecast
            # Need to estimate the FCF in the first year after forecast for GGM
            if num_forecast_years > 0 and base_free_cash_flows[num_forecast_years - 1] > 0:
                fcf_next_year = base_free_cash_flows[num_forecast_years - 1] * (1 + growth_rate)
                if discount_rate > growth_rate:
                    terminal_value = fcf_next_year / (discount_rate - growth_rate)
                else:
                    terminal_value = 0 # Or use a very large number to indicate problem
            
            # Also calculate using exit multiple based on last FCF of forecast period if applicable.
            if num_forecast_years > 0:
                terminal_value_multiple = base_free_cash_flows[num_forecast_years - 1] * exit_multiple
            else:
                terminal_value_multiple = 0.0
            
            # Choose the higher of the two or a weighted average etc. For simplicity, use multiple if available.
            terminal_value = terminal_value_multiple if terminal_value_multiple > 0 else terminal_value

        else: # Should be caught by validation, but as a safeguard
            terminal_value = 0

        # Discount terminal value to present
        pv_terminal_value = terminal_value / ((1 + discount_rate)**exit_year) # Discount back to t=0

        simulated_valuations[i] = pv_explicit_fcf + pv_terminal_value

    mean_valuation = np.mean(simulated_valuations)
    median_valuation = np.median(simulated_valuations)
    
    valuation_percentiles = {
        '5th': np.percentile(simulated_valuations, 5),
        '25th': np.percentile(simulated_valuations, 25),
        '75th': np.percentile(simulated_valuations, 75),
        '95th': np.percentile(simulated_valuations, 95)
    }

    return {
        'simulated_valuations': simulated_valuations,
        'mean_valuation': mean_valuation,
        'median_valuation': median_valuation,
        'valuation_percentiles': valuation_percentiles
    }