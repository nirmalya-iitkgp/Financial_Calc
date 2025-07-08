# financial_calculator/utils/helper_functions.py

import logging
from typing import Union
import re
from config import DEFAULT_DECIMAL_PLACES_CURRENCY, DEFAULT_DECIMAL_PLACES_PERCENTAGE, DEFAULT_DECIMAL_PLACES_GENERAL

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def format_currency(amount: Union[float, int], currency_symbol: str = "$", decimal_places: int = DEFAULT_DECIMAL_PLACES_CURRENCY, include_symbol: bool = True) -> str:
    """
    Formats a numeric amount as a currency string.

    Args:
        amount (Union[float, int]): The numerical amount to format.
        currency_symbol (str): The symbol of the currency (e.g., "$", "€", "₹").
        decimal_places (int): The number of decimal places to format to.
                                Defaults to DEFAULT_DECIMAL_PLACES_CURRENCY from config.
        include_symbol (bool): If True, the currency symbol is included in the output.
                                Defaults to True. <-- ADD THIS LINE TO DOCSTRING

    Returns:
        str: The formatted currency string.
    """
    try:
        # Ensure amount is a float for consistent formatting
        float_amount = float(amount)

        # Format the number with specified decimal places and thousands separator
        # This uses f-string for comma separation and decimal places directly.
        formatted_amount_with_commas = f"{float_amount:,.{decimal_places}f}"

        if include_symbol:
            return f"{currency_symbol}{formatted_amount_with_commas}"
        else:
            return formatted_amount_with_commas

    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting currency amount {amount} with symbol '{currency_symbol}': {e}")
        return f"Error: Invalid Amount"
# --- END OF CHANGE ---

def format_percentage(value: Union[float, int], decimal_places: int = DEFAULT_DECIMAL_PLACES_PERCENTAGE) -> str:
    """
    Formats a decimal value (e.g., 0.05) as a percentage string (e.g., "5.00%").

    Args:
        value (Union[float, int]): The decimal value to format.
        decimal_places (int): The number of decimal places for the percentage.
                              Defaults to DEFAULT_DECIMAL_PLACES_PERCENTAGE from config.

    Returns:
        str: The formatted percentage string.
    """
    try:
        # Multiply by 100 to get percentage value
        percentage_value = value * 100
        # Format the percentage value
        format_string = f"{{:.{decimal_places}f}}%"
        return format_string.format(percentage_value)
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting percentage value {value}: {e}")
        return "Error: Invalid Percentage"

def format_number(value: Union[float, int], decimal_places: int = DEFAULT_DECIMAL_PLACES_GENERAL) -> str:
    """
    Formats a general numeric value to a specified number of decimal places.

    Args:
        value (Union[float, int]): The numerical value to format.
        decimal_places (int): The number of decimal places.
                              Defaults to DEFAULT_DECIMAL_PLACES_GENERAL from config.

    Returns:
        str: The formatted number string.
    """
    try:
        format_string = f"{{:,.{decimal_places}f}}"
        return format_string.format(value)
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting number {value}: {e}")
        return "Error: Invalid Number"


# --- Example Usage (for testing purposes, won't run when imported) ---
if __name__ == '__main__':
    # Test currency formatting
    print("--- Testing format_currency ---")
    print(f"1234.5678 (default $): {format_currency(1234.5678)}")
    print(f"987654.321 (€, 2dp): {format_currency(987654.321, '€', 2)}")
    print(f"100.0 (₹, 0dp): {format_currency(100.0, '₹', 0)}")
    print(f"-500.25 ($, 3dp): {format_currency(-500.25, '$', 3)}")
    print(f"0 (default $): {format_currency(0)}")
    print(f"'abc' (error): {format_currency('abc')}")

    # Test percentage formatting
    print("\n--- Testing format_percentage ---")
    print(f"0.05 (default dp): {format_percentage(0.05)}")
    print(f"0.123456 (2dp): {format_percentage(0.123456, 2)}")
    print(f"1.0 (0dp): {format_percentage(1.0, 0)}")
    print(f"-0.025 (1dp): {format_percentage(-0.025, 1)}")
    print(f"10 (for 1000%): {format_percentage(10)}") # Large percentage
    print(f"'xyz' (error): {format_percentage('xyz')}")

    # Test general number formatting
    print("\n--- Testing format_number ---")
    print(f"12345.6789 (default dp): {format_number(12345.6789)}")
    print(f"123.456 (2dp): {format_number(123.456, 2)}")
    print(f"1000000 (0dp): {format_number(1000000, 0)}")
    print(f"-987.654321 (4dp): {format_number(-987.654321, 4)}")
    print(f"'pqr' (error): {format_number('pqr')}")