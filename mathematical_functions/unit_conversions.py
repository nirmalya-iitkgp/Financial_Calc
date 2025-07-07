# mathematical_functions/unit_conversions.py

def convert_time_periods(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts a time value from one unit to another based on predefined conversion ratios.

    Args:
        value (float): The numerical value to convert. Must be non-negative.
        from_unit (str): The unit of the input value (e.g., 'days', 'weeks', 'months', 'quarters', 'years').
                         Case-insensitive.
        to_unit (str): The desired unit for the output value (e.g., 'days', 'weeks', 'months', 'quarters', 'years').
                       Case-insensitive.

    Returns:
        float: The converted value in the 'to_unit'.

    Raises:
        ValueError: If `value` is negative, if `from_unit` or `to_unit` are invalid/unsupported.

    Assumptions/Limitations for Consistency with Tests:
    - 1 week = 7 days (exact)
    - 1 year = 365 days (approximation for days-to-year and year-to-days)
    - 1 year = 12 months (exact)
    - 1 year = 4 quarters (exact)
    - Implications:
        - 1 month is approximately 365 / 12 = 30.4166... days.
        - 1 quarter is approximately 365 / 4 = 91.25 days.
        - This model prioritizes exact relationships for years/months/quarters
          and week/day conversions, resulting in fractional days for months/quarters.
    """
    if value < 0:
        raise ValueError("Time value to convert cannot be negative.")

    # Define conversion factors for each unit relative to 'days'
    # These factors are chosen to satisfy the exact relationships implied by the tests.
    days_per_unit = {
        'days': 1.0,
        'weeks': 7.0,
        'months': 365.0 / 12.0,  # To ensure 1 year = 12 months AND 1 year = 365 days
        'quarters': 365.0 / 4.0, # To ensure 1 year = 4 quarters AND 1 year = 365 days
        'years': 365.0,
    }

    from_unit_lower = from_unit.lower()
    to_unit_lower = to_unit.lower()

    if from_unit_lower not in days_per_unit:
        raise ValueError(f"Unsupported 'from_unit': {from_unit}. Supported units are: {list(days_per_unit.keys())}")
    if to_unit_lower not in days_per_unit:
        raise ValueError(f"Unsupported 'to_unit': {to_unit}. Supported units are: {list(days_per_unit.keys())}")

    # Convert the 'value' from its 'from_unit' to a base unit (days)
    value_in_days = value * days_per_unit[from_unit_lower]

    # Convert the value from the base unit (days) to the 'to_unit'
    converted_value = value_in_days / days_per_unit[to_unit_lower]

    return converted_value