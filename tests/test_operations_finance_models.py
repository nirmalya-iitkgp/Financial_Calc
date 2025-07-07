# tests/test_operations_finance_models.py

import pytest
import math
from mathematical_functions.operations_finance_models import (
    calculate_eoq,
    calculate_reorder_point,
    calculate_newsvendor_optimal_quantity,
    calculate_cascaded_pricing_protection_levels
)
# --- Tests for calculate_eoq ---

@pytest.mark.parametrize(
    "annual_demand, ordering_cost, holding_cost, expected_eoq, expected_total_cost",
    [
        (12000, 100, 10, 489.8979, 4898.979),  # Basic case
        (100, 10, 1, 44.7214, 44.7214),       # Simpler numbers
        (1000, 50, 5, 141.4214, 707.1068),    # Another case
        (1, 1, 1, 1.4142, 1.4142),            # Edge: all ones
    ]
)
def test_calculate_eoq_valid_inputs(annual_demand, ordering_cost, holding_cost, expected_eoq, expected_total_cost):
    """Test calculate_eoq with valid inputs."""
    result = calculate_eoq(annual_demand, ordering_cost, holding_cost)
    assert "error" not in result
    assert math.isclose(result["eoq"], expected_eoq, rel_tol=1e-4)
    assert math.isclose(result["total_annual_cost"], expected_total_cost, rel_tol=1e-4)

@pytest.mark.parametrize(
    "annual_demand, ordering_cost, holding_cost",
    [
        (0, 100, 10),      # Zero demand
        (12000, 0, 10),    # Zero ordering cost
        (12000, 100, 0),   # Zero holding cost (division by zero risk)
        (-100, 100, 10),   # Negative demand
        (12000, -100, 10), # Negative ordering cost
        (12000, 100, -10), # Negative holding cost
        ("abc", 100, 10),  # Non-numeric demand
        (12000, None, 10), # None ordering cost
    ]
)
def test_calculate_eoq_invalid_inputs(annual_demand, ordering_cost, holding_cost):
    """Test calculate_eoq with invalid inputs, expecting an error."""
    result = calculate_eoq(annual_demand, ordering_cost, holding_cost)
    assert "error" in result
    assert isinstance(result["error"], str)


# --- Tests for calculate_reorder_point ---

@pytest.mark.parametrize(
    "daily_demand, lead_time_days, service_level, std_dev_daily_demand, expected_rop, expected_ss",
    [
        # Corrected expected values based on recalculation
        (10, 5, 0.95, 2, 57.350, 7.350),     # Standard case
        (10, 5, 0.5, 2, 50.0, 0.0),        # Service level 0.5 (no safety stock)
        (10, 5, 0.99, 0, 50.0, 0.0),       # Zero std dev (no safety stock)
        (1, 1, 0.9, 0.5, 1.6407, 0.6407),    # Small numbers
        (100, 10, 0.999, 5, 1048.859, 48.859), # High service level, higher demand
    ]
)
def test_calculate_reorder_point_valid_inputs(daily_demand, lead_time_days, service_level, std_dev_daily_demand, expected_rop, expected_ss):
    """Test calculate_reorder_point with valid inputs."""
    result = calculate_reorder_point(daily_demand, lead_time_days, service_level, std_dev_daily_demand)
    assert "error" not in result
    assert math.isclose(result["reorder_point"], expected_rop, rel_tol=1e-2) # Relaxed tolerance due to Z-score precision
    assert math.isclose(result["safety_stock"], expected_ss, rel_tol=1e-2)

@pytest.mark.parametrize(
    "daily_demand, lead_time_days, service_level, std_dev_daily_demand",
    [
        (-10, 5, 0.95, 2),     # Negative daily demand
        (10, -5, 0.95, 2),     # Negative lead time
        (10, 5, 1.1, 2),       # Service level > 1
        (10, 5, -0.1, 2),      # Service level < 0
        (10, 5, 0.95, -2),     # Negative std dev
        ("abc", 5, 0.95, 2),   # Non-numeric daily demand
        (10, 5, "xyz", 2),     # Non-numeric service level
    ]
)
def test_calculate_reorder_point_invalid_inputs(daily_demand, lead_time_days, service_level, std_dev_daily_demand):
    """Test calculate_reorder_point with invalid inputs, expecting an error."""
    result = calculate_reorder_point(daily_demand, lead_time_days, service_level, std_dev_daily_demand)
    assert "error" in result
    assert isinstance(result["error"], str)


# --- Tests for calculate_newsvendor_optimal_quantity ---

@pytest.mark.parametrize(
    "cu, co, demand_type, demand_params, expected_cr, expected_oq, expected_el, expected_es",
    [
        # Normal Distribution Tests (corrected EL/ES)
        (10, 90, 'normal', {'mean': 100, 'std_dev': 10}, 0.1, 87.184, 0.477, 13.293), # CR 0.1, Z=-1.28
        (50, 50, 'normal', {'mean': 100, 'std_dev': 10}, 0.5, 100.0, 3.989, 3.989),  # CR 0.5, Z=0
        (90, 10, 'normal', {'mean': 100, 'std_dev': 10}, 0.9, 112.816, 13.293, 0.477), # CR 0.9, Z=1.28
        (10, 90, 'normal', {'mean': 100, 'std_dev': 0}, 0.1, 100.0, 0.0, 0.0),     # Zero std dev (should be 100, 0, 0)
        (1, 1, 'normal', {'mean': 50, 'std_dev': 5}, 0.5, 50.0, 1.994, 1.994),

        # Uniform Distribution Tests (corrected EL/ES)
        (10, 90, 'uniform', {'min': 50, 'max': 150}, 0.1, 60.0, 0.5, 40.5),      # CR 0.1
        (50, 50, 'uniform', {'min': 50, 'max': 150}, 0.5, 100.0, 12.5, 12.5),    # CR 0.5
        (90, 10, 'uniform', {'min': 50, 'max': 150}, 0.9, 140.0, 40.5, 0.5),      # CR 0.9
        (10, 90, 'uniform', {'min': 100, 'max': 100}, 0.1, 100.0, 0.0, 0.0),    # Min=Max (certain demand)
    ]
)
def test_calculate_newsvendor_valid_inputs(cu, co, demand_type, demand_params, expected_cr, expected_oq, expected_el, expected_es):
    """Test calculate_newsvendor_optimal_quantity with valid inputs."""
    result = calculate_newsvendor_optimal_quantity(cu, co, demand_type, demand_params)
    assert "error" not in result
    assert math.isclose(result["critical_ratio"], expected_cr, rel_tol=1e-4)
    assert math.isclose(result["optimal_quantity"], expected_oq, rel_tol=1e-2) # Relaxed for PPF
    if expected_el is not None:
        assert math.isclose(result["expected_leftover"], expected_el, rel_tol=1e-2)
    if expected_es is not None:
        assert math.isclose(result["expected_stockout"], expected_es, rel_tol=1e-2)

@pytest.mark.parametrize(
    "cu, co, demand_type, demand_params",
    [
        (0, 10, 'normal', {'mean': 100, 'std_dev': 10}), # Zero Cu
        (10, 0, 'normal', {'mean': 100, 'std_dev': 10}), # Zero Co
        (-10, 10, 'normal', {'mean': 100, 'std_dev': 10}), # Negative Cu
        (10, -10, 'normal', {'mean': 100, 'std_dev': 10}), # Negative Co
        (10, 10, 'invalid', {'mean': 100, 'std_dev': 10}), # Invalid demand type
        (10, 10, 'normal', {'mean': -100, 'std_dev': 10}), # Negative normal mean (now correctly caught by validation)
        (10, 10, 'normal', {'mean': 100, 'std_dev': -10}), # Negative normal std dev
        (10, 10, 'normal', {'std_dev': 10}), # Missing normal mean
        (10, 10, 'uniform', {'min': -50, 'max': 150}), # Negative uniform min
        (10, 10, 'uniform', {'min': 150, 'max': 50}), # Uniform min > max
        (10, 10, 'uniform', {'min': 50}), # Missing uniform max
    ]
)
def test_calculate_newsvendor_invalid_inputs(cu, co, demand_type, demand_params):
    """Test calculate_newsvendor_optimal_quantity with invalid inputs, expecting an error."""
    result = calculate_newsvendor_optimal_quantity(cu, co, demand_type, demand_params)
    assert "error" in result
    assert isinstance(result["error"], str)


# --- Tests for calculate_cascaded_pricing_protection_levels ---

@pytest.mark.parametrize(
    "total_capacity, fare_classes, expected_protection_levels",
    [
        # Two Classes, Standard Case (P1 > P2) - Corrected expected values
        (100, [
            {'price': 200, 'demand_mean': 30, 'demand_std_dev': 10, 'name': 'First'},
            {'price': 100, 'demand_mean': 80, 'demand_std_dev': 20, 'name': 'Economy'}
        ], [30.0, 0.0]), # Q_F (protect F from E) = norm.ppf(1 - 100/200, 30, 10) = 30.0

        # Three Classes, Standard Case (P1 > P2 > P3) - Corrected expected values
        (200, [
            {'price': 300, 'demand_mean': 20, 'demand_std_dev': 5, 'name': 'First'},
            {'price': 200, 'demand_mean': 50, 'demand_std_dev': 10, 'name': 'Business'},
            {'price': 100, 'demand_mean': 100, 'demand_std_dev': 20, 'name': 'Economy'}
        ], [70.0, 70.0, 0.0]), # P_L for Bus=70 (protect F+B from E); P_L for First=70 (max(calc_F, P_L_Bus))

        # Two Classes, Capacity constraint - Expected behavior unchanged if limits are below capacity
        (50, [
            {'price': 200, 'demand_mean': 30, 'demand_std_dev': 10, 'name': 'First'},
            {'price': 100, 'demand_mean': 80, 'demand_std_dev': 20, 'name': 'Economy'}
        ], [30.0, 0.0]),

        # Single Class (should default to 0 protection for itself)
        (100, [
            {'price': 150, 'demand_mean': 70, 'demand_std_dev': 15, 'name': 'Standard'}
        ], [0.0]),

        # Zero std dev demands - Corrected expected values
        (100, [
            {'price': 200, 'demand_mean': 30, 'demand_std_dev': 0, 'name': 'First'},
            {'price': 100, 'demand_mean': 70, 'demand_std_dev': 0, 'name': 'Economy'}
        ], [30.0, 0.0]), # Protect exactly the mean if std_dev is 0.

        # With original_index to ensure output order - Corrected expected values
        (100, [
            {'price': 100, 'demand_mean': 80, 'demand_std_dev': 20, 'name': 'Economy'}, # Original index 0
            {'price': 200, 'demand_mean': 30, 'demand_std_dev': 10, 'name': 'First'},   # Original index 1
        ], [0.0, 30.0]), # Output should match original input order: [Economy_Prot, First_Prot]
    ]
)
def test_calculate_cascaded_pricing_valid_inputs(total_capacity, fare_classes, expected_protection_levels):
    """Test calculate_cascaded_pricing_protection_levels with valid inputs."""
    result = calculate_cascaded_pricing_protection_levels(total_capacity, fare_classes)
    assert "error" not in result
    
    # Assert protection levels matching expected values
    assert len(result["protection_levels"]) == len(expected_protection_levels)
    for i in range(len(expected_protection_levels)):
        assert math.isclose(result["protection_levels"][i], expected_protection_levels[i], rel_tol=1e-2)

@pytest.mark.parametrize(
    "total_capacity, fare_classes",
    [
        (0, [{'price': 100, 'demand_mean': 50, 'demand_std_dev': 10}]), # Zero capacity
        (-10, [{'price': 100, 'demand_mean': 50, 'demand_std_dev': 10}]), # Negative capacity
        (100, []), # Empty fare_classes list
        (100, "not a list"), # Invalid fare_classes type
        (100, [{}]), # Missing fare class keys
        (100, [{'price': -100, 'demand_mean': 50, 'demand_std_dev': 10}]), # Negative price
        (100, [{'price': 100, 'demand_mean': -50, 'demand_std_dev': 10}]), # Negative mean demand
        (100, [{'price': 100, 'demand_mean': 50, 'demand_std_dev': -10}]), # Negative std dev demand
        (100, [{'price': 100, 'demand_mean': "abc", 'demand_std_dev': 10}]), # Non-numeric demand param
        # MOVED FROM VALID INPUTS: Duplicate prices (now correctly flagged as error by validation)
        (100, [
            {'price': 100, 'demand_mean': 30, 'demand_std_dev': 10, 'name': 'First'},
            {'price': 100, 'demand_mean': 80, 'demand_std_dev': 20, 'name': 'Economy'}
        ]),
    ]
)
def test_calculate_cascaded_pricing_invalid_inputs(total_capacity, fare_classes):
    """Test calculate_cascaded_pricing_protection_levels with invalid inputs, expecting an error."""
    result = calculate_cascaded_pricing_protection_levels(total_capacity, fare_classes)
    assert "error" in result
    assert isinstance(result["error"], str)