# financial_calculator/utils/validation.py

import logging
from typing import Union, List, Dict

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def validate_numeric_input(value: str, field_name: str = "Input") -> tuple[bool, float | str]:
    """
    Validates if a string can be converted to a float.

    Args:
        value (str): The string input from the GUI.
        field_name (str): The name of the input field for better error messages.

    Returns:
        tuple[bool, float | str]: (True, float_value) if valid, (False, error_message) otherwise.
    """
    if not value.strip():
        return False, f"{field_name} cannot be empty."
    try:
        numeric_value = float(value)
        return True, numeric_value
    except ValueError:
        logger.warning(f"Validation failed for '{field_name}': '{value}' is not a valid number.")
        return False, f"{field_name} must be a valid number."

def validate_positive_numeric_input(value: str, field_name: str = "Input") -> tuple[bool, float | str]:
    """
    Validates if a string can be converted to a float and is strictly positive (> 0).

    Args:
        value (str): The string input from the GUI.
        field_name (str): The name of the input field for better error messages.

    Returns:
        tuple[bool, float | str]: (True, float_value) if valid and positive, (False, error_message) otherwise.
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value # Pass along the error from numeric validation

    # Check if it's actually a number after the initial validation
    if not isinstance(numeric_value, (int, float)): 
        return False, f"Internal error: {field_name} validation result is not numeric."

    if numeric_value <= 0:
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be positive.")
        return False, f"{field_name} must be a positive number."
    return True, numeric_value

def validate_non_negative_numeric_input(value: str, field_name: str = "Input") -> tuple[bool, float | str]:
    """
    Validates if a string can be converted to a float and is non-negative (>= 0).

    Args:
        value (str): The string input from the GUI.
        field_name (str): The name of the input field for better error messages.

    Returns:
        tuple[bool, float | str]: (True, float_value) if valid and non-negative, (False, error_message) otherwise.
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value # Pass along the error from numeric validation

    # Check if it's actually a number after the initial validation
    if not isinstance(numeric_value, (int, float)): 
        return False, f"Internal error: {field_name} validation result is not numeric."

    if numeric_value < 0:
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be non-negative.")
        return False, f"{field_name} must be a non-negative number."
    return True, numeric_value

def validate_percentage_input(value: str, field_name: str = "Rate") -> tuple[bool, float | str]:
    """
    Validates if a string can be converted to a float and is interpreted as a percentage (e.g., 0.0 to 1.0).
    Assumes input like "0.05" for 5%.

    Args:
        value (str): The string input from the GUI.
        field_name (str): The name of the input field for better error messages.

    Returns:
        tuple[bool, float | str]: (True, float_value) if valid, (False, error_message) otherwise.
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value # Pass along the error from numeric validation

    # Check if it's actually a number after the initial validation
    if not isinstance(numeric_value, (int, float)): 
        return False, f"Internal error: {field_name} validation result is not numeric."

    # As per your existing comment, this specifically allows any float,
    # as conversion to 0-1 range typically happens in the calculation logic.
    return True, numeric_value


def validate_list_input(input_str: str, expected_type: str, field_name: str) -> tuple[bool, list | str]:
    """
    Validates a comma-separated string of inputs and converts them to a list
    of the specified type (numeric or string).

    Args:
        input_str (str): The string to validate (e.g., "1,2,3.5,4" or "item1,item2").
        expected_type (str): 'numeric' for numbers, 'string' for text.
        field_name (str): The name of the input field for error messages.

    Returns:
        tuple[bool, list | str]: (True, list_of_validated_values) if valid,
                                (False, error_message) otherwise.
    """
    if not input_str.strip():
        logger.warning(f"Validation failed for '{field_name}': Input list cannot be empty.")
        return False, f"{field_name} cannot be empty."

    # Split by comma, strip whitespace from each item, and filter out any empty strings
    # that might result from extra commas (e.g., "1,,2").
    items = [item.strip() for item in input_str.split(',') if item.strip()]

    if not items:
        logger.warning(f"Validation failed for '{field_name}': No valid entries found after splitting by comma.")
        return False, f"{field_name} contains no valid entries (check for only commas or spaces)."

    validated_list = []
    if expected_type == 'numeric':
        for item in items:
            is_valid, numeric_value = validate_numeric_input(item, f"item in {field_name}")
            if not is_valid:
                # Return the specific error message from validate_numeric_input
                logger.warning(f"Validation failed for '{field_name}': {numeric_value}")
                return False, numeric_value
            validated_list.append(numeric_value)
        return True, validated_list
    elif expected_type == 'string':
        # For string lists, just return the stripped items
        return True, items
    else:
        logger.error(f"Internal error: Unsupported validation type '{expected_type}' requested for list input '{field_name}'.")
        return False, f"Internal error: Invalid validation type for {field_name}."
        
def validate_numeric_range(value: str, min_val: Union[int, float], max_val: Union[int, float], field_name: str = "Input") -> tuple[bool, float | str]:
    """
    Validates if a string can be converted to a float and falls within a specified inclusive range.

    Args:
        value (str): The string input from the GUI.
        min_val (Union[int, float]): The minimum allowed value (inclusive).
        max_val (Union[int, float]): The maximum allowed value (inclusive).
        field_name (str): The name of the input field for better error messages.

    Returns:
        tuple[bool, float | str]: (True, float_value) if valid and in range, (False, error_message) otherwise.
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value # Pass along the error from numeric validation

    if not (min_val <= numeric_value <= max_val):
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be between {min_val} and {max_val}.")
        return False, f"{field_name} must be between {min_val} and {max_val}."
    return True, numeric_value

def validate_positive_integer_input(value: str, field_name: str = "Input") -> tuple[bool, int | str]:
    """
    Validates if a string can be converted to an integer and is strictly positive (> 0).
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value

    if not float(numeric_value).is_integer(): # Check if it's an integer after converting to float
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be a whole number.")
        return False, f"{field_name} must be a whole number."

    integer_value = int(numeric_value)
    if integer_value <= 0:
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be a positive integer.")
        return False, f"{field_name} must be a positive integer."
    return True, integer_value

def validate_non_negative_integer_input(value: str, field_name: str = "Input") -> tuple[bool, int | str]:
    """
    Validates if a string can be converted to an integer and is non-negative (>= 0).
    """
    is_valid, numeric_value = validate_numeric_input(value, field_name)
    if not is_valid:
        return is_valid, numeric_value

    if not float(numeric_value).is_integer(): # Check if it's an integer after converting to float
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be a whole number.")
        return False, f"{field_name} must be a whole number."

    integer_value = int(numeric_value)
    if integer_value < 0: # This is the key difference from positive_integer
        logger.warning(f"Validation failed for '{field_name}': '{value}' must be a non-negative integer.")
        return False, f"{field_name} must be a non-negative integer."
    return True, integer_value

def validate_newsvendor_demand_params(demand_type: str, demand_params: dict) -> tuple[bool, dict | str]:
    """
    Validates demand parameters for Newsvendor model.
    Checks logical consistency of parameters based on demand type.

    Args:
        demand_type (str): 'normal' or 'uniform'.
        demand_params (dict): Dictionary of parameters
                              (e.g., {'mean': ..., 'std_dev': ...} or {'min': ..., 'max': ...}).
                              Assumes individual numeric values within this dict are already floats/ints.

    Returns:
        tuple[bool, dict | str]: (True, validated_demand_params) if valid,
                                 (False, error_message) otherwise.
    """
    if not isinstance(demand_type, str) or not demand_type:
        logger.warning("Validation failed: Newsvendor demand_type must be a non-empty string.")
        return False, "Demand type cannot be empty."

    if not isinstance(demand_params, dict):
        logger.warning("Validation failed: Newsvendor demand_params must be a dictionary.")
        return False, "Demand parameters must be provided as a dictionary."

    demand_type_lower = demand_type.lower()

    if demand_type_lower == 'normal':
        mean = demand_params.get('mean')
        std_dev = demand_params.get('std_dev')

        if mean is None or std_dev is None:
            logger.warning("Validation failed: Normal demand requires 'Mean (μ)' and 'Std Dev (σ)' parameters.")
            return False, "Normal demand requires 'Mean (μ)' and 'Std Dev (σ)' parameters."
        
        if not isinstance(mean, (int, float)) or not isinstance(std_dev, (int, float)):
            logger.warning(f"Validation failed: Mean ('{mean}') and Std Dev ('{std_dev}') must be numeric for normal demand.")
            return False, "Mean and Std Dev for normal demand must be numbers."

        # ADDED THIS LINE: Validate that mean demand is non-negative
        if mean < 0:
            logger.warning(f"Validation failed: Mean demand for normal distribution cannot be negative (got {mean}).")
            return False, "Mean demand for normal distribution cannot be negative."

        if std_dev < 0:
            logger.warning(f"Validation failed: Standard deviation for normal demand cannot be negative (got {std_dev}).")
            return False, "Standard deviation for normal demand cannot be negative."

    elif demand_type_lower == 'uniform':
        min_d = demand_params.get('min')
        max_d = demand_params.get('max')

        if min_d is None or max_d is None:
            logger.warning("Validation failed: Uniform demand requires 'Min Demand' and 'Max Demand' parameters.")
            return False, "Uniform demand requires 'Min Demand' and 'Max Demand' parameters."
        
        if not isinstance(min_d, (int, float)) or not isinstance(max_d, (int, float)):
            logger.warning(f"Validation failed: Min Demand ('{min_d}') and Max Demand ('{max_d}') must be numeric for uniform demand.")
            return False, "Min and Max Demand for uniform demand must be numbers."

        if min_d < 0 or max_d < 0:
            logger.warning(f"Validation failed: Min ({min_d}) and Max ({max_d}) Demand for Uniform distribution cannot be negative.")
            return False, "Min and Max Demand for Uniform distribution cannot be negative."

        if min_d > max_d:
            logger.warning(f"Validation failed: Min Demand ({min_d}) must be less than or equal to Max Demand ({max_d}) for Uniform distribution.")
            return False, "Min Demand must be less than or equal to Max Demand for Uniform distribution."
    else:
        logger.warning(f"Validation failed: Unsupported demand type '{demand_type}' for Newsvendor model.")
        return False, f"Unsupported demand type: '{demand_type}'. Choose 'normal' or 'uniform'."
    
    return True, demand_params

def validate_fare_classes(fare_classes: List[Dict[str, Union[float, str]]]) -> tuple[bool, List[Dict[str, Union[float, str]]] | str]:
    """
    Validates a list of fare class dictionaries for Cascaded Pricing.
    Performs logical and structural checks on the list and its elements.

    Args:
        fare_classes (List[Dict]): List of fare classes, each with expected keys like 'price',
                                   'demand_mean', 'demand_std_dev'.
                                   Assumes individual numeric values within each dict are already floats/ints.

    Returns:
        tuple[bool, List[Dict] | str]: (True, validated_fare_classes) if valid,
                                       (False, error_message) otherwise.
    """
    if not isinstance(fare_classes, list):
        logger.warning("Validation failed: Fare classes input must be a list.")
        return False, "Fare classes must be provided as a list."

    if not fare_classes:
        logger.warning("Validation failed: At least one fare class must be provided for Cascaded Pricing.")
        return False, "At least one fare class must be provided for Cascaded Pricing."

    prices_seen = set()
    for i, fc in enumerate(fare_classes):
        if not isinstance(fc, dict):
            logger.warning(f"Validation failed: Fare class entry {i+1} is not a dictionary.")
            return False, f"Fare class entry {i+1} is malformed; it must be a dictionary."

        # Check for required keys
        required_keys = ['price', 'demand_mean', 'demand_std_dev']
        if not all(k in fc for k in required_keys):
            missing_keys = [k for k in required_keys if k not in fc]
            logger.warning(f"Validation failed: Fare Class {i+1} is missing required keys: {', '.join(missing_keys)}.")
            return False, f"Fare Class {i+1} is missing required keys: {', '.join(missing_keys)}."
        
        # Validate types and values
        price = fc['price']
        demand_mean = fc['demand_mean']
        demand_std_dev = fc['demand_std_dev']

        if not isinstance(price, (int, float)):
            logger.warning(f"Validation failed: Fare Class {i+1} price '{price}' must be numeric.")
            return False, f"Fare Class {i+1} price must be a number."
        if price <= 0:
            logger.warning(f"Validation failed: Fare Class {i+1} price ({price}) must be positive.")
            return False, f"Fare Class {i+1} price must be positive."
        # Keep this check: Prices must be unique.
        if price in prices_seen:
            logger.warning(f"Validation failed: Fare Class {i+1} has a duplicate price of {price}. Prices must be unique.")
            return False, f"Fare Class {i+1} has a duplicate price of {price}. Prices must be unique."
        prices_seen.add(price)

        if not isinstance(demand_mean, (int, float)):
            logger.warning(f"Validation failed: Fare Class {i+1} demand mean '{demand_mean}' must be numeric.")
            return False, f"Fare Class {i+1} demand mean must be a number."
        if demand_mean < 0:
            logger.warning(f"Validation failed: Fare Class {i+1} demand mean ({demand_mean}) cannot be negative.")
            return False, f"Fare Class {i+1} demand mean cannot be negative."

        if not isinstance(demand_std_dev, (int, float)):
            logger.warning(f"Validation failed: Fare Class {i+1} demand standard deviation '{demand_std_dev}' must be numeric.")
            return False, f"Fare Class {i+1} demand standard deviation must be a number."
        if demand_std_dev < 0:
            logger.warning(f"Validation failed: Fare Class {i+1} demand standard deviation ({demand_std_dev}) cannot be negative.")
            return False, f"Fare Class {i+1} demand standard deviation cannot be negative."
    
    return True, fare_classes
# --- Example Usage (for testing purposes, won't run when imported) ---
if __name__ == '__main__':
    print("--- Testing complted ---")