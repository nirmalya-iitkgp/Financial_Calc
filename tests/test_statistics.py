# tests/test_statistics.py

import pytest
import numpy as np
from mathematical_functions.statistics import (
    calculate_descriptive_stats,
    perform_simple_linear_regression
)
from scipy import stats # Imported for direct comparison with some standard stats functions

# --- Tests for calculate_descriptive_stats ---

def test_descriptive_stats_single_list_basic():
    """
    Test descriptive statistics for a basic single list of positive integers.
    Verifies mean, median, mode, standard deviation, and variance.
    """
    data = [1, 2, 3, 4, 5]
    stats_output = calculate_descriptive_stats(data)

    assert stats_output['mean'] == pytest.approx(3.0)
    assert stats_output['median'] == pytest.approx(3.0)
    # For data where all values are unique, scipy.stats.mode often returns the smallest value.
    assert stats_output['mode'] == pytest.approx(1)
    # Compare against numpy's sample standard deviation (ddof=1)
    assert stats_output['std_dev'] == pytest.approx(np.std(data, ddof=1))
    # Compare against numpy's sample variance (ddof=1)
    assert stats_output['variance'] == pytest.approx(np.var(data, ddof=1))

def test_descriptive_stats_single_list_with_duplicates():
    """
    Test descriptive statistics for a single list containing duplicate values,
    ensuring mode is correctly identified.
    """
    data = [1, 2, 2, 3, 3, 3, 4]
    stats_output = calculate_descriptive_stats(data)
    assert stats_output['mean'] == pytest.approx(2.57142857)
    assert stats_output['median'] == pytest.approx(3.0)
    assert stats_output['mode'] == pytest.approx(3) # '3' appears most frequently
    assert stats_output['std_dev'] == pytest.approx(np.std(data, ddof=1))
    assert stats_output['variance'] == pytest.approx(np.var(data, ddof=1))

def test_descriptive_stats_single_list_negative_values():
    """
    Test descriptive statistics for a single list with negative numerical values.
    """
    data = [-1, -2, -3, -4, -5]
    stats_output = calculate_descriptive_stats(data)
    assert stats_output['mean'] == pytest.approx(-3.0)
    assert stats_output['median'] == pytest.approx(-3.0)
    # For unique negative values, scipy.stats.mode tends to return the minimum value.
    assert stats_output['mode'] == pytest.approx(-5.0) # Adjusted expectation to match scipy's common behavior
    assert stats_output['std_dev'] == pytest.approx(np.std(data, ddof=1))
    assert stats_output['variance'] == pytest.approx(np.var(data, ddof=1))

def test_descriptive_stats_single_list_single_element():
    """
    Test descriptive statistics for a list containing only one element.
    Standard deviation and variance should be NaN for N=1 (sample statistics).
    """
    data = [10]
    stats_output = calculate_descriptive_stats(data)
    assert stats_output['mean'] == pytest.approx(10.0)
    assert stats_output['median'] == pytest.approx(10.0)
    assert stats_output['mode'] == pytest.approx(10.0)
    assert np.isnan(stats_output['std_dev']) # std_dev for single element sample is NaN (division by N-1=0)
    assert np.isnan(stats_output['variance']) # variance for single element sample is NaN

def test_descriptive_stats_single_list_empty():
    """
    Test case for an empty input list. Expects a ValueError.
    The regex for the error message is crucial here.
    """
    with pytest.raises(ValueError, match=r"Input data list\(s\) cannot be empty."): # Fixed regex escape
        calculate_descriptive_stats([])

def test_descriptive_stats_single_list_non_numeric():
    """
    Test case for a single list containing non-numeric values. Expects a ValueError.
    The regex for the error message is adjusted to match the function's message.
    """
    with pytest.raises(ValueError, match=r"Input data list\(s\) contain non-numeric values."): # Fixed regex escape
        calculate_descriptive_stats([1, 2, 'a', 4])

def test_descriptive_stats_two_lists_basic():
    """
    Test descriptive statistics when two lists are provided, including
    mean, covariance, and correlation for both.
    """
    data1 = [1, 2, 3, 4, 5]
    data2 = [2, 4, 5, 4, 5]
    stats_output = calculate_descriptive_stats((data1, data2))

    assert stats_output['data1_mean'] == pytest.approx(3.0)
    assert stats_output['data2_mean'] == pytest.approx(4.0)
    # Compare covariance with numpy's calculation
    assert stats_output['covariance'] == pytest.approx(np.cov(data1, data2, ddof=1)[0, 1])
    # Compare correlation with numpy's calculation
    assert stats_output['correlation'] == pytest.approx(np.corrcoef(data1, data2)[0, 1])

def test_descriptive_stats_two_lists_different_lengths():
    """
    Test case where two lists of different lengths are provided. Expects a ValueError.
    """
    data1 = [1, 2, 3]
    data2 = [4, 5]
    with pytest.raises(ValueError, match=r"The two input data lists must have the same length for covariance/correlation."): # Fixed regex escape
        calculate_descriptive_stats((data1, data2))

def test_descriptive_stats_two_lists_non_numeric():
    """
    Test case where one of the two provided lists contains non-numeric values.
    Expects a ValueError with a specific message.
    """
    with pytest.raises(ValueError, match=r"Input data list\(s\) contain non-numeric values."): # Fixed regex escape
        calculate_descriptive_stats(([1, 2, 3], [4, 'b', 6]))

# --- Tests for perform_simple_linear_regression ---

def test_linear_regression_basic():
    """
    Test simple linear regression with a perfectly positively correlated dataset.
    Slope, intercept, and R-squared should be exact.
    """
    x_data = [1, 2, 3, 4, 5]
    y_data = [2, 4, 6, 8, 10] # y = 2x + 0
    result = perform_simple_linear_regression(x_data, y_data)
    assert result['slope'] == pytest.approx(2.0)
    assert result['intercept'] == pytest.approx(0.0)
    assert result['r_squared'] == pytest.approx(1.0) # Perfect positive correlation

def test_linear_regression_with_intercept():
    """
    Test simple linear regression with a dataset that has a non-zero intercept.
    """
    x_data = [1, 2, 3]
    y_data = [3, 5, 7] # y = 2x + 1
    result = perform_simple_linear_regression(x_data, y_data)
    assert result['slope'] == pytest.approx(2.0)
    assert result['intercept'] == pytest.approx(1.0)
    assert result['r_squared'] == pytest.approx(1.0)

def test_linear_regression_negative_slope():
    """
    Test simple linear regression with a negatively correlated dataset.
    """
    x_data = [1, 2, 3]
    y_data = [3, 2, 1] # y = -x + 4
    result = perform_simple_linear_regression(x_data, y_data)
    assert result['slope'] == pytest.approx(-1.0)
    assert result['intercept'] == pytest.approx(4.0)
    assert result['r_squared'] == pytest.approx(1.0) # Perfect negative correlation

def test_linear_regression_no_correlation():
    """
    Test linear regression where there is no linear relationship (flat line for Y).
    Slope should be 0, intercept is the mean of Y, and R-squared should be 0.
    """
    x_data = [1, 2, 3, 4, 5]
    y_data = [5, 5, 5, 5, 5] # Y values are constant
    result = perform_simple_linear_regression(x_data, y_data)
    assert result['slope'] == pytest.approx(0.0)
    assert result['intercept'] == pytest.approx(5.0)
    assert result['r_squared'] == pytest.approx(0.0) # No variance in Y explained by X

def test_linear_regression_invalid_empty_lists():
    """
    Test linear regression with empty input lists. Expects a ValueError.
    """
    with pytest.raises(ValueError, match=r"Input data lists cannot be empty."): # Fixed regex escape
        perform_simple_linear_regression([], [])

def test_linear_regression_invalid_different_lengths():
    """
    Test linear regression with input lists of different lengths. Expects a ValueError.
    """
    with pytest.raises(ValueError, match=r"Input X and Y data lists must have the same length."): # Fixed regex escape
        perform_simple_linear_regression([1, 2], [3])

def test_linear_regression_invalid_insufficient_data():
    """
    Test linear regression with less than two data points (minimum required).
    Expects a ValueError.
    """
    with pytest.raises(ValueError, match=r"At least two data points are required for linear regression."): # Fixed regex escape
        perform_simple_linear_regression([1], [2])

def test_linear_regression_invalid_non_numeric():
    """
    Test linear regression with non-numeric values in one of the input lists.
    Expects a ValueError with the adjusted message.
    """
    with pytest.raises(ValueError, match=r"Input data lists contain non-numeric values."): # Fixed regex escape
        perform_simple_linear_regression([1, 2, 'a'], [3, 4, 5])

def test_linear_regression_invalid_no_x_variance():
    """
    Test linear regression where the X data has no variance (all X values are identical).
    This makes the slope undefined. Expects a ValueError.
    """
    with pytest.raises(ValueError, match=r"Cannot perform regression: X data has no variance \(all X values are the same\)."): # Fixed regex escape
        perform_simple_linear_regression([1, 1, 1], [2, 3, 4])