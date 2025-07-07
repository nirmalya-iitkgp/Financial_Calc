# mathematical_functions/forex.py

def convert_currency(amount: float, spot_rate_from_to: float) -> float:
    """
    Converts a given amount from one currency to another using a direct spot rate.

    Args:
        amount (float): The amount of the 'from' currency to convert. Must be non-negative.
        spot_rate_from_to (float): The spot exchange rate. This rate should represent
                                   'Units of the 'To' Currency per 1 Unit of the 'From' Currency'.
                                   For example, if converting USD to EUR, and 1 USD = 0.92 EUR,
                                   then spot_rate_from_to would be 0.92. Must be positive.

    Returns:
        float: The converted amount in the 'to' currency.

    Raises:
        ValueError: If amount is negative or spot_rate_from_to is not positive.

    Assumptions/Limitations:
    - This function performs a simple direct conversion, assuming the provided spot rate
      is the correct one for the desired conversion direction.
    - Does not account for bid-ask spreads, transaction fees, or real-time market data.
    """
    if amount < 0:
        raise ValueError("Amount to convert cannot be negative.")
    if spot_rate_from_to <= 0:
        raise ValueError("Spot rate must be positive.")
    
    converted_amount = amount * spot_rate_from_to
    return converted_amount

def calculate_forward_rate(
    spot_rate: float,
    domestic_interest_rate: float,
    foreign_interest_rate: float,
    time_to_maturity_years: float
) -> float:
    """
    Calculates the theoretical forward exchange rate based on interest rate parity.

    Args:
        spot_rate (float): The current spot exchange rate (e.g., USD/EUR, meaning units of foreign per 1 unit of domestic).
                           Must be positive.
        domestic_interest_rate (float): The annualized risk-free interest rate in the domestic currency (as a decimal).
                                        Must be > -1.
        foreign_interest_rate (float): The annualized risk-free interest rate in the foreign currency (as a decimal).
                                       Must be > -1.
        time_to_maturity_years (float): The time to maturity of the forward contract in years. Must be positive.

    Returns:
        float: The calculated theoretical forward exchange rate.

    Raises:
        ValueError: If spot_rate is non-positive, time_to_maturity_years is non-positive,
                    or if either interest rate is less than or equal to -1.

    Assumptions/Limitations:
    - Assumes interest rate parity holds.
    - Interest rates are assumed to be compounded in a manner consistent with the formula,
      or compounded discretely in the same frequency as time_to_maturity.
      (Commonly, continuous compounding is assumed for simplicity in theory. If discrete, ensure consistency.)
      Using the common discrete compounding formula here:
      Forward Rate = Spot Rate * (1 + Domestic Rate * T) / (1 + Foreign Rate * T) for simple interest,
      or Forward Rate = Spot Rate * (1 + Domestic Rate)^T / (1 + Foreign Rate)^T for annual compounding.
      Let's use the annual compounding version as it's more common for rates in practice.
      For continuous, it'd be Spot * exp((rd - rf) * T)

      Given common use cases, the discrete annual compounding is often implied:
      F = S * [(1 + r_domestic)^T / (1 + r_foreign)^T]
    """
    if spot_rate <= 0:
        raise ValueError("Spot rate must be positive.")
    if time_to_maturity_years <= 0:
        raise ValueError("Time to maturity must be positive.")
    # Interest rates can be negative in some economic conditions, but for typical parity,
    # (1+r) must not be zero or negative, so r must be > -1.
    if domestic_interest_rate <= -1 or foreign_interest_rate <= -1:
        raise ValueError("Interest rates must be greater than -1 (or -100%).")

    # Assuming annual compounding for interest rates
    forward_rate = spot_rate * ((1 + domestic_interest_rate)**time_to_maturity_years /
                                (1 + foreign_interest_rate)**time_to_maturity_years)
    return forward_rate