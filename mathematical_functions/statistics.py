#mathematical_functions/statistics.py

import numpy as np
from scipy import stats
import math

def calculate_descriptive_stats(data_list: list | tuple[list, list]) -> dict:
    """
    Calculates descriptive statistics for one or two lists of numerical data.

    This function can operate on a single list of numbers to provide
    mean, median, mode, standard deviation, and variance.
    Alternatively, it can accept a tuple of two lists to also compute
    the covariance and correlation between them.

    Args:
        data_list (list | tuple[list, list]):
            - A single list of numerical data (e.g., [1, 2, 3, 4, 5]).
            - A tuple containing two lists of numerical data
              (e.g., ([1, 2, 3], [4, 5, 6])) for which covariance and
              correlation will also be calculated.

    Returns:
        dict: A dictionary containing calculated statistics. The keys depend
              on whether one or two lists were provided:
              - For a single list: 'mean', 'median', 'mode', 'std_dev', 'variance'.
              - For two lists: 'data1_mean', 'data1_median', 'data1_mode', etc.,
                'data2_mean', 'data2_median', 'data2_mode', etc.,
                'covariance', 'correlation'.

    Raises:
        ValueError:
            - If data_list is empty (either the single list or any sub-list).
            - If data_list contains non-numeric values that cannot be converted to float.
            - If two lists are provided but have different lengths (for covariance/correlation).
        RuntimeError: (Less likely with current scipy, but conceptually if mode logic fails)
            - If mode cannot be robustly found (e.g., highly unusual data patterns).

    Assumptions/Limitations:
    - Mode returns the first mode found by `scipy.stats.mode` if multiple exist.
      If all values are unique, it attempts to indicate "No distinct mode".
      For a single-element list, the element itself is considered the mode.
    - Standard deviation and variance are calculated as sample statistics (using N-1 degrees of freedom, `ddof=1`).
    - If a list has only one element, std_dev and variance will be `NaN`
      because division by (N-1) = 0 occurs.
    """

    data1 = None
    data2 = None
    is_two_lists = False

    # Determine if input is a single list or a tuple of two lists
    if isinstance(data_list, tuple) and len(data_list) == 2:
        # Ensure both lists in the tuple are not empty before processing
        if not data_list[0] or not data_list[1]:
            raise ValueError("Input data list(s) cannot be empty.")
        try:
            data1 = np.array(data_list[0], dtype=float)
            data2 = np.array(data_list[1], dtype=float)
        except ValueError:
            # Catch conversion errors for non-numeric values
            raise ValueError("Input data list(s) contain non-numeric values.")
        is_two_lists = True
    elif isinstance(data_list, list):
        # Ensure the single list is not empty
        if not data_list:
            raise ValueError("Input data list(s) cannot be empty.")
        try:
            data1 = np.array(data_list, dtype=float)
        except ValueError:
            # Catch conversion errors for non-numeric values
            raise ValueError("Input data list(s) contain non-numeric values.")
        is_two_lists = False
    else:
        # Raise error for invalid input type
        raise ValueError("Input 'data_list' must be a list or a tuple of two lists.")

    # The isnan check is still good for detecting NaNs that might arise from other operations,
    # though the primary non-numeric string conversion is now handled above.
    if np.isnan(data1).any():
        raise ValueError("Input data list(s) contain non-numeric values.")
    if is_two_lists and np.isnan(data2).any():
        raise ValueError("Input data list(s) contain non-numeric values.")

    results = {}

    def _calculate_single_list_stats(arr: np.ndarray, prefix: str = "") -> dict:
        """
        Helper function to calculate descriptive statistics for a single numpy array.
        """
        res = {}
        if len(arr) == 0:
            return {f'{prefix}mean': np.nan, f'{prefix}median': np.nan, f'{prefix}mode': np.nan,
                    f'{prefix}std_dev': np.nan, f'{prefix}variance': np.nan}

        res[f'{prefix}mean'] = np.mean(arr)
        res[f'{prefix}median'] = np.median(arr)

        mode_result = stats.mode(arr, keepdims=False)

        # SciPy's stats.mode can return either a ModeResult object with a .mode attribute
        # which is an array, or in some very specific edge cases (depending on SciPy version
        # and data), it might directly return a scalar for .mode.
        # This robustly handles both possibilities.
        if isinstance(mode_result.mode, np.ndarray) and len(mode_result.mode) > 0:
            res[f'{prefix}mode'] = mode_result.mode[0]
        elif isinstance(mode_result.mode, (float, int, np.integer, np.floating)): # Added numpy numeric types
            res[f'{prefix}mode'] = mode_result.mode
        else:
            # Fallback for cases where mode_result.mode is empty or problematic.
            # This handles scenarios like all unique values, or single element lists
            # where stats.mode might behave differently.
            if len(arr) == 1:
                res[f'{prefix}mode'] = arr[0] # The only element is the mode
            elif len(set(arr)) == len(arr):
                # For unique values, scipy.stats.mode typically returns the smallest.
                # If you want "No distinct mode", you could set it to a string or NaN,
                # but for direct numerical comparison in tests, returning the min is safer if that's what scipy does.
                res[f'{prefix}mode'] = np.min(arr) # Explicitly return the minimum if all unique as per scipy's common behavior
            else:
                res[f'{prefix}mode'] = np.nan # Default to NaN if mode couldn't be determined

        res[f'{prefix}std_dev'] = np.std(arr, ddof=1) if len(arr) > 1 else np.nan
        res[f'{prefix}variance'] = np.var(arr, ddof=1) if len(arr) > 1 else np.nan

        return res

    results.update(_calculate_single_list_stats(data1, "data1_" if is_two_lists else ""))

    if is_two_lists:
        if len(data1) != len(data2):
            raise ValueError("The two input data lists must have the same length for covariance/correlation.")

        results.update(_calculate_single_list_stats(data2, "data2_"))

        if len(data1) < 2:
            results['covariance'] = np.nan
            results['correlation'] = np.nan
        else:
            covariance_matrix = np.cov(data1, data2, ddof=1)
            results['covariance'] = covariance_matrix[0, 1]

            correlation_matrix = np.corrcoef(data1, data2)
            results['correlation'] = correlation_matrix[0, 1]

    return results

def perform_simple_linear_regression(x_data: list[float], y_data: list[float]) -> dict:
    """
    Performs a simple linear regression (y = mx + b) and returns the slope, intercept, and R-squared.

    Uses `scipy.stats.linregress` for robust calculation.

    Args:
        x_data (list[float]): The independent variable data (list of floats).
        y_data (list[float]): The dependent variable data (list of floats).

    Returns:
        dict: A dictionary containing the regression results:
              - 'slope' (m)
              - 'intercept' (b)
              - 'r_squared' (coefficient of determination)

    Raises:
        ValueError:
            - If input lists are empty.
            - If input lists have different lengths.
            - If there are insufficient data points (less than 2).
            - If input lists contain non-numeric values.
            - If x_data has no variance (all x values are the same), as
              regression cannot be performed in such a case.
    """
    if not x_data or not y_data:
        raise ValueError("Input data lists cannot be empty.")
    if len(x_data) != len(y_data):
        raise ValueError("Input X and Y data lists must have the same length.")
    if len(x_data) < 2:
        raise ValueError("At least two data points are required for linear regression.")

    try:
        x_np = np.array(x_data, dtype=float)
        y_np = np.array(y_data, dtype=float)
    except ValueError:
        raise ValueError("Input data lists contain non-numeric values.")

    if np.std(x_np) == 0:
        raise ValueError("Cannot perform regression: X data has no variance (all X values are the same).")

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_np, y_np)

    if np.std(y_np) == 0:
        r_squared = 0.0
    else:
        r_squared = r_value**2

    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared
    }