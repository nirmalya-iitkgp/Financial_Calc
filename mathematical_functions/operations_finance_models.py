# financial_calculator/models/operations_finance_models.py

import math
from scipy.stats import norm
import logging
from utils.validation import validate_newsvendor_demand_params, validate_fare_classes

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def calculate_eoq(annual_demand: float, ordering_cost_per_order: float, holding_cost_per_unit_per_year: float) -> dict:
    """
    Calculates the Economic Order Quantity (EOQ) and total annual cost.

    Args:
        annual_demand (float): Total annual demand (D).
        ordering_cost_per_order (float): Fixed cost per order (S).
        holding_cost_per_unit_per_year (float): Holding cost per unit per year (H).

    Returns:
        dict: 'eoq', 'total_annual_cost'. Returns 'error' key on invalid input/exception.
    """
    # KEEP THIS: These are basic type/value checks.
    # While GUI will pre-validate, these act as a robust safeguard if called directly.
    if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [annual_demand, ordering_cost_per_order, holding_cost_per_unit_per_year]):
        logger.error("EOQ failed: All inputs must be positive numbers.")
        return {"error": "All inputs for EOQ must be positive numbers."}

    try:
        eoq = math.sqrt((2 * annual_demand * ordering_cost_per_order) / holding_cost_per_unit_per_year)
        total_annual_cost = (annual_demand / eoq) * ordering_cost_per_order + (eoq / 2) * holding_cost_per_unit_per_year
        return {"eoq": eoq, "total_annual_cost": total_annual_cost}
    except Exception as e:
        logger.error(f"Error calculating EOQ: {e}")
        return {"error": f"An unexpected error occurred during EOQ calculation: {e}"}

def calculate_reorder_point(daily_demand: float, lead_time_days: float, service_level: float, std_dev_daily_demand: float = 0) -> dict:
    """
    Calculates the Reorder Point (ROP) and Safety Stock.

    Args:
        daily_demand (float): Average daily demand.
        lead_time_days (float): Lead time in days.
        service_level (float): Desired service level (0.0 to 1.0).
        std_dev_daily_demand (float, optional): Standard deviation of daily demand. Defaults to 0.

    Returns:
        dict: 'reorder_point', 'safety_stock'. Returns 'error' key on invalid input/exception.
    """
    # KEEP THESE: Similar to EOQ, these are basic type/range checks for individual parameters.
    if not all(isinstance(arg, (int, float)) and arg >= 0 for arg in [daily_demand, lead_time_days, std_dev_daily_demand]):
        logger.error("ROP failed: Daily demand, lead time, and std dev must be non-negative numbers.")
        return {"error": "Daily demand, lead time, and std dev must be non-negative numbers."}
    if not (isinstance(service_level, (int, float)) and 0 <= service_level <= 1):
        logger.error("ROP failed: Service level must be between 0 and 1.")
        return {"error": "Service level must be between 0 and 1."}

    try:
        demand_during_lead_time = daily_demand * lead_time_days
        safety_stock = 0.0

        if std_dev_daily_demand > 0 and service_level > 0.5:
            z_score = norm.ppf(service_level)
            std_dev_lead_time_demand = math.sqrt(lead_time_days) * std_dev_daily_demand
            safety_stock = z_score * std_dev_lead_time_demand
        elif std_dev_daily_demand == 0 and service_level > 0.5: # Clarify case where SS is 0
            logger.info("Service level > 0.5 but Std Dev Daily Demand is 0. Safety stock will be 0.")

        reorder_point = demand_during_lead_time + safety_stock
        return {"reorder_point": reorder_point, "safety_stock": safety_stock}
    except Exception as e:
        logger.error(f"Error calculating ROP: {e}")
        return {"error": f"An unexpected error occurred during Reorder Point calculation: {e}"}


def calculate_newsvendor_optimal_quantity(cost_understock: float, cost_overstock: float,
                                          demand_type: str, demand_params: dict) -> dict:
    """
    Calculates the optimal order quantity for the Newsvendor Model.

    Args:
        cost_understock (float): Cost incurred for demand not met (Cu). Must be positive.
        cost_overstock (float): Cost incurred for unsold units (Co). Must be positive.
        demand_type (str): Demand distribution type ('normal' or 'uniform').
        demand_params (dict): Parameters for demand distribution.
                              - 'normal': {'mean': float, 'std_dev': float}
                              - 'uniform': {'min': float, 'max': float}

    Returns:
        dict: 'critical_ratio', 'optimal_quantity', 'expected_leftover', 'expected_stockout'.
              Returns 'error' key on invalid input/exception.
    """
    # KEEP THIS: Basic check for direct costs.
    if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [cost_understock, cost_overstock]):
        logger.error("Newsvendor failed: Understock and Overstock costs must be positive.")
        return {"error": "Understock and Overstock costs must be positive numbers."}

    # NEW: Validate demand_params using the centralized function
    is_valid_demand, validated_demand_params_or_error = validate_newsvendor_demand_params(demand_type, demand_params)
    if not is_valid_demand:
        logger.error(f"Newsvendor failed: Demand parameters validation error: {validated_demand_params_or_error}")
        return {"error": validated_demand_params_or_error}
    
    # Use the potentially corrected/validated demand_params
    # Note: Our validation function returns the original dict if valid, so this is safe.
    # For clarity, we can re-assign to original variable name if desired, or just use `demand_params`
    # demand_params = validated_demand_params_or_error # No, because the original demand_params is already good if valid.

    critical_ratio = cost_understock / (cost_understock + cost_overstock)
    optimal_quantity = 0.0
    expected_leftover = None
    expected_stockout = None

    try:
        # The following checks for mean_demand, std_dev_demand, min_demand, max_demand
        # (type, non-negativity, min <= max) are now handled by validate_newsvendor_demand_params
        # So, we can access them directly as they are guaranteed to be valid if we reached here.

        if demand_type.lower() == 'normal':
            mean_demand = demand_params['mean'] # Safe to access directly after validation
            std_dev_demand = demand_params['std_dev'] # Safe to access directly

            if std_dev_demand == 0:
                optimal_quantity = mean_demand # Deterministic demand
                expected_stockout = max(0, mean_demand - optimal_quantity)
                expected_leftover = max(0, optimal_quantity - mean_demand)
            else:
                optimal_quantity = norm.ppf(critical_ratio, loc=mean_demand, scale=std_dev_demand)
                z_star = (optimal_quantity - mean_demand) / std_dev_demand
                expected_stockout = std_dev_demand * (norm.pdf(z_star) - z_star * (1 - norm.cdf(z_star)))
                expected_leftover = std_dev_demand * (norm.pdf(z_star) + z_star * norm.cdf(z_star))

        elif demand_type.lower() == 'uniform':
            min_demand = demand_params['min'] # Safe to access directly
            max_demand = demand_params['max'] # Safe to access directly
            
            # The min_demand > max_demand check is now handled by validate_newsvendor_demand_params
            # The min_demand == max_demand deterministic case remains here as it's part of the calculation logic
            if min_demand == max_demand:
                optimal_quantity = min_demand
                expected_leftover = max(0, optimal_quantity - min_demand)
                expected_stockout = max(0, min_demand - optimal_quantity)
            else:
                optimal_quantity = min_demand + critical_ratio * (max_demand - min_demand)
                if optimal_quantity >= max_demand:
                    expected_leftover = optimal_quantity - (min_demand + max_demand) / 2
                    expected_stockout = 0
                elif optimal_quantity <= min_demand:
                    expected_leftover = 0
                    expected_stockout = (min_demand + max_demand) / 2 - optimal_quantity
                else:
                    expected_leftover = (optimal_quantity - min_demand)**2 / (2 * (max_demand - min_demand))
                    expected_stockout = (max_demand - optimal_quantity)**2 / (2 * (max_demand - min_demand))
        # The 'else: Unsupported demand type' check is now handled by validate_newsvendor_demand_params
        # So, this block is removed.
        
        return {
            "critical_ratio": critical_ratio,
            "optimal_quantity": optimal_quantity,
            "expected_leftover": expected_leftover,
            "expected_stockout": expected_stockout
        }
    except Exception as e:
        logger.error(f"Error calculating Newsvendor: {e}")
        return {"error": f"An unexpected error occurred during Newsvendor calculation: {e}"}


def calculate_cascaded_pricing_protection_levels(total_capacity: float, fare_classes: list) -> dict:
    """
    Calculates optimal protection levels (booking limits) for multiple fare classes
    using an EMSR-a like approach for independent normal demands.

    Args:
        total_capacity (float): Total available capacity. Must be positive.
        fare_classes (list): List of dicts, each with:
                              - 'price': float (higher prices first is recommended, but code sorts)
                              - 'demand_mean': float (Mean of demand for this class)
                              - 'demand_std_dev': float (Std dev of demand for this class)
                              - 'name' (optional): str for logging/debugging

    Returns:
        dict: 'protection_levels' (booking limits for each class in original input order).
              Returns 'error' key on invalid input/exception.
    """
    # KEEP THIS: Basic check for total_capacity.
    if not isinstance(total_capacity, (int, float)) or total_capacity <= 0:
        logger.error("Cascaded Pricing failed: Total capacity must be a positive number.")
        return {"error": "Total capacity must be a positive number."}
    
    # NEW: Validate fare_classes using the centralized function
    is_valid_fare_classes, validated_fare_classes_or_error = validate_fare_classes(fare_classes)
    if not is_valid_fare_classes:
        logger.error(f"Cascaded Pricing failed: Fare classes validation error: {validated_fare_classes_or_error}")
        return {"error": validated_fare_classes_or_error}

    # Use the potentially corrected/validated fare_classes for the rest of the logic
    # Note: Our validation function returns the original list if valid.
    # fare_classes = validated_fare_classes_or_error # No, original is already fine if valid.

    # Store original index to return results in original order (keep this)
    # This must be done BEFORE sorting to preserve original order mapping.
    for idx, fc in enumerate(fare_classes):
        fc['original_index'] = idx
    
    try:
        # Sort fare classes by price in descending order for calculation logic
        # This step can raise KeyError if 'price' is missing (but validate_fare_classes should prevent this now)
        # Or TypeError if price is not comparable (also prevented by validation)
        # So, the try-except here becomes a general safeguard, rather than primary validation.
        sorted_fare_classes = sorted(fare_classes, key=lambda x: x['price'], reverse=True)
    except Exception as e: # Broaden to catch any unexpected sorting issues, though less likely now
        logger.error(f"Cascaded Pricing failed during sorting: {e}")
        return {"error": f"An unexpected error occurred during fare class sorting: {e}"}

    # REMOVE THE FOLLOWING BLOCK: It's now handled by validate_fare_classes
    # for i, fc in enumerate(sorted_fare_classes):
    #     if not all(k in fc for k in ['price', 'demand_mean', 'demand_std_dev']):
    #         logger.error(f"Cascaded Pricing failed: Fare class {i+1} missing required keys.")
    #         return {"error": f"Fare class {i+1} is missing required parameters."}
    #     if not (isinstance(fc['price'], (int, float)) and fc['price'] > 0):
    #         logger.error(f"Cascaded Pricing failed: Fare class {i+1} price must be positive.")
    #         return {"error": f"Fare class {i+1} price must be positive."}
    #     if not (isinstance(fc['demand_mean'], (int, float)) and fc['demand_mean'] >= 0):
    #         logger.error(f"Cascaded Pricing failed: Fare class {i+1} demand mean must be non-negative.")
    #         return {"error": f"Fare class {i+1} demand mean must be non-negative."}
    #     if not (isinstance(fc['demand_std_dev'], (int, float)) and fc['demand_std_dev'] >= 0):
    #         logger.error(f"Cascaded Pricing failed: Fare class {i+1} demand std dev must be non-negative.")
    #         return {"error": f"Fare class {i+1} demand std dev must be non-negative."}

    num_classes = len(sorted_fare_classes)
    # booking_limits[i] = total units to protect for classes with index 0 to i (highest prices)
    booking_limits_temp = [0.0] * num_classes

    try:
        # Lowest price class (last in sorted list) has a booking limit of 0.
        booking_limits_temp[num_classes - 1] = 0.0

        # Iterate from the second lowest price class up to the highest price class (index 0)
        # This calculates booking_limits[i] (for class i and all higher-priced classes).
        for i in range(num_classes - 2, -1, -1):
            current_fc_sorted = sorted_fare_classes[i] # Higher price class in current comparison
            next_lower_fc_sorted = sorted_fare_classes[i+1] # Lower price class for comparison (opportunity cost)

            price_higher = current_fc_sorted['price']
            price_lower = next_lower_fc_sorted['price']

            # Sum of demands for the current class AND all classes ABOVE it (for this bundle)
            combined_mean_for_bl = sum(fc['demand_mean'] for fc in sorted_fare_classes[:i+1])
            combined_variance_for_bl = sum(fc['demand_std_dev']**2 for fc in sorted_fare_classes[:i+1])
            combined_std_dev_for_bl = math.sqrt(combined_variance_for_bl)

            if price_higher <= price_lower:
                logger.warning(f"Price for class '{current_fc_sorted.get('name', 'N/A')}' ({price_higher}) is not strictly higher than class '{next_lower_fc_sorted.get('name', 'N/A')}' ({price_lower}). Setting calculated limit to 0.")
                calculated_limit = 0.0
            elif combined_std_dev_for_bl == 0:
                calculated_limit = combined_mean_for_bl
            else:
                # Probability threshold for norm.ppf: P(Demand for higher bundle > Q) = P_lower / P_higher
                # So, CDF(Q) = 1 - (P_lower / P_higher)
                prob_threshold = 1 - (price_lower / price_higher)
                prob_threshold = max(0.0001, min(0.9999, prob_threshold)) # Clamp to avoid ppf errors
                calculated_limit = norm.ppf(prob_threshold, loc=combined_mean_for_bl, scale=combined_std_dev_for_bl)
            
            # Booking limit for class `i` ensures nesting: it's the max of its calculated limit
            # and the booking limit for the next higher class (i+1).
            booking_limits_temp[i] = max(0.0, calculated_limit, booking_limits_temp[i+1]) # Ensure non-negative and nested

        # Reorder booking limits to match original input order
        final_ordered_protection_levels = [0.0] * num_classes
        for i, fc in enumerate(sorted_fare_classes):
            original_idx = fc['original_index']
            final_ordered_protection_levels[original_idx] = booking_limits_temp[i]

        return {
            "protection_levels": final_ordered_protection_levels,
            "expected_revenue": None # Complex to calculate accurately without simulation/more inputs
        }
    except Exception as e:
        logger.error(f"Error calculating Cascaded Pricing: {e}")
        return {"error": f"An unexpected error occurred during Cascaded Pricing calculation: {e}"}