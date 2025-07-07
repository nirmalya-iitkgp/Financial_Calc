# mathematical_functions/accounting.py

def calculate_depreciation_straight_line(cost: float, salvage_value: float, useful_life_years: int) -> float:
    """
    Calculates the annual depreciation expense using the Straight-Line method.

    Args:
        cost (float): The initial cost of the asset. Must be positive.
        salvage_value (float): The estimated residual value of the asset at the end of its useful life.
                               Must be non-negative and less than or equal to `cost`.
        useful_life_years (int): The estimated number of years the asset will be used. Must be a positive integer.

    Returns:
        float: The annual depreciation expense.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive cost or useful life, salvage value > cost).

    Assumptions/Limitations:
    - Depreciation expense is constant each year.
    - Asset is used for the full useful life.
    """
    if cost <= 0:
        raise ValueError("Asset cost must be positive.")
    if salvage_value < 0:
        raise ValueError("Salvage value cannot be negative.")
    if salvage_value > cost:
        # Adjusted error message to precisely match the test's regex pattern
        raise ValueError("Salvage value cannot be greater than the asset cost.")
    if not isinstance(useful_life_years, int) or useful_life_years <= 0:
        raise ValueError("Useful life in years must be a positive integer.")
    
    depreciable_base = cost - salvage_value
    annual_depreciation = depreciable_base / useful_life_years
    
    return annual_depreciation

def calculate_depreciation_double_declining_balance(cost: float, salvage_value: float, useful_life_years: int, current_year: int) -> float:
    """
    Calculates the depreciation expense for a specific year using the Double-Declining Balance (DDB) method.

    Args:
        cost (float): The initial cost of the asset. Must be positive.
        salvage_value (float): The estimated residual value of the asset at the end of its useful life.
                               Must be non-negative and less than or equal to `cost`.
        useful_life_years (int): The estimated number of years the asset will be used. Must be a positive integer.
        current_year (int): The specific year for which to calculate depreciation (1-based, e.g., 1 for the first year).
                            Must be a positive integer and not exceed useful_life_years.

    Returns:
        float: The depreciation expense for the specified `current_year`.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive cost or useful life, salvage value > cost,
                    or invalid current_year).

    Assumptions/Limitations:
    - Switches to straight-line depreciation when straight-line depreciation on the remaining book value
      exceeds the DDB depreciation, or when book value is close to salvage value to prevent
      depreciating below salvage value.
    - Asset is used for the full useful life.
    """
    # --- Input Validation ---
    if cost <= 0:
        raise ValueError("Asset cost must be positive.")
    if salvage_value < 0:
        raise ValueError("Salvage value cannot be negative.")
    if salvage_value > cost:
        # Adjusted error message to precisely match the test's regex pattern
        raise ValueError("Salvage value cannot be greater than the asset cost.")
    if not isinstance(useful_life_years, int) or useful_life_years <= 0:
        raise ValueError("Useful life in years must be a positive integer.")
    
    if not isinstance(current_year, int):
        # Adjusted error message to precisely match the test's regex pattern
        raise ValueError("Current year must be a positive integer and not exceed useful_life_years.")
    if current_year <= 0:
        # Adjusted error message to precisely match the test's regex pattern
        raise ValueError("Current year must be a positive integer and not exceed useful_life_years.")
    if current_year > useful_life_years:
        # No depreciation after the useful life
        return 0.0

    # --- DDB Calculation Logic with Switch to Straight-Line ---
    ddb_rate = 2.0 / useful_life_years
    current_book_value = cost
    
    depreciation_for_current_year = 0.0

    # Simulate depreciation year by year up to the current_year
    for year_num in range(1, useful_life_years + 1):
        if current_book_value <= salvage_value:
            # Asset fully depreciated or reached salvage value in a prior year
            current_book_value = salvage_value
            if year_num == current_year: # If this is the specific year asked, return 0
                return 0.0
            continue # Continue loop to update book value for subsequent years if needed, though depreciation is 0

        # Calculate DDB depreciation for the current iteration year
        ddb_depreciation = ddb_rate * current_book_value

        # Calculate remaining useful life for straight-line switch
        remaining_useful_life = useful_life_years - year_num + 1

        # Calculate straight-line depreciation on remaining depreciable base
        if remaining_useful_life > 0:
            straight_line_depreciation_on_remaining = (current_book_value - salvage_value) / remaining_useful_life
        else:
            straight_line_depreciation_on_remaining = 0.0 

        # Choose the larger of DDB or straight-line (this is the "switch")
        chosen_depreciation = max(ddb_depreciation, straight_line_depreciation_on_remaining)
        
        # Cap depreciation to ensure book value does not go below salvage value
        if (current_book_value - chosen_depreciation) < salvage_value:
            chosen_depreciation = current_book_value - salvage_value
            
        # Ensure depreciation is not negative
        chosen_depreciation = max(0.0, chosen_depreciation)

        if year_num == current_year:
            depreciation_for_current_year = chosen_depreciation
            break # Found the depreciation for the requested current_year

        current_book_value -= chosen_depreciation
        
        # Explicitly ensure book value does not fall below salvage_value after deduction
        if current_book_value < salvage_value:
            current_book_value = salvage_value
            

    return depreciation_for_current_year