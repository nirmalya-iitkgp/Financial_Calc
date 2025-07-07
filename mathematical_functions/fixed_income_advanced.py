# mathematical_functions/fixed_income_advanced.py

import math
import numpy as np

def calculate_macaulay_duration(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the Macaulay Duration of a coupon-paying bond.
    Macaulay Duration is the weighted average time until a bond's cash flows are received.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year.

    Returns:
        float: The Macaulay Duration of the bond in years.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive face value, years, or frequency,
                    negative rates, or if bond price becomes zero/undefined).
    """
    # --- Input Validations ---
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if coupon_rate < 0:
        raise ValueError("Coupon rate cannot be negative.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if not isinstance(compounding_freq_per_year, int) or compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be a positive integer.")
    # Yield to maturity can be negative in real markets, but not below -1 (-100%)
    if yield_to_maturity < -1:
        raise ValueError("Yield to maturity cannot be less than -1 (or -100%).")

        # --- Calculations Setup ---
    periodic_coupon_payment = (face_value * coupon_rate) / compounding_freq_per_year
    periodic_yield = yield_to_maturity / compounding_freq_per_year
    total_periods = int(n_years * compounding_freq_per_year)

    if total_periods == 0:
        return 0.0

    pv_of_cash_flows_sum = 0.0
    weighted_pv_cash_flows_sum = 0.0

    # Iterate through each period to calculate PV of cash flows and weighted PV
    for i in range(1, total_periods + 1):
        # Calculate cash flow for the current period (coupon payment)
        current_cash_flow = periodic_coupon_payment

        # Add face value to the last cash flow period
        if i == total_periods:
            current_cash_flow += face_value

        # Discount factor
        if periodic_yield == 0:
            discount_factor = 1.0
        else:
            discount_factor = 1 / ((1 + periodic_yield) ** i)
        
        pv_cf = current_cash_flow * discount_factor
        pv_of_cash_flows_sum += pv_cf
        weighted_pv_cash_flows_sum += pv_cf * i # Weighted by period 'i'

    # --- Handle effectively zero bond price (denominator) ---
    # Define dynamic tolerance based on face_value: 0.05% of face_value, with a minimum of 1e-9.
    # This means if the bond price is less than 0.05% of its face value (or 1e-9, whichever is larger),
    # it is considered effectively zero.
    effectively_zero_threshold = max(face_value * 0.00051, 1e-9) # 0.05% of face value, or min 1e-9
    
    if math.isclose(pv_of_cash_flows_sum, 0.0, abs_tol=effectively_zero_threshold):
        raise ValueError("Bond price (sum of PV of cash flows) is effectively zero, Macaulay duration is undefined.")

    # --- Final Calculation ---
    macaulay_duration_periods = weighted_pv_cash_flows_sum / pv_of_cash_flows_sum
    macaulay_duration_years = macaulay_duration_periods / compounding_freq_per_year
    
    return macaulay_duration_years


def calculate_convexity(face_value: float, coupon_rate: float, yield_to_maturity: float, n_years: float, compounding_freq_per_year: int) -> float:
    """
    Calculates the Convexity of a coupon-paying bond.
    Convexity measures the curvature of the bond's price-yield relationship,
    indicating how bond price sensitivity changes with yield changes.

    Args:
        face_value (float): The par value or maturity value of the bond.
        coupon_rate (float): The annual coupon rate (as a decimal).
        yield_to_maturity (float): The annual yield to maturity (as a decimal).
        n_years (float): The number of years until the bond matures.
        compounding_freq_per_year (int): Number of times interest is compounded/coupons are paid per year.

    Returns:
        float: The Convexity of the bond in years squared.

    Raises:
        ValueError: If inputs are invalid (e.g., non-positive face value, years, or frequency,
                    negative rates, or if bond price becomes zero/undefined).
    """
    # --- Input Validations ---
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if coupon_rate < 0:
        raise ValueError("Coupon rate cannot be negative.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")
    if not isinstance(compounding_freq_per_year, int) or compounding_freq_per_year <= 0:
        raise ValueError("Compounding frequency per year must be a positive integer.")
    if yield_to_maturity < -1:
        raise ValueError("Yield to maturity cannot be less than -1 (or -100%).")
    # Special case for 0 YTM in convexity, as the formula involves (1+y)^4 etc.,
    # and division by (1+y)^2 and so on. This implementation doesn't handle y=0 gracefully for convexity.
    if math.isclose(yield_to_maturity, 0.0, abs_tol=1e-9): # Use a small tolerance for exact zero YTM
         raise ValueError("Convexity calculation is not precisely defined for zero yield to maturity in this implementation.")

    # --- Calculations Setup ---
    sum_convexity_numerator_terms = 0.0
    bond_price_denominator = 0.0

    periodic_coupon_payment = (face_value * coupon_rate) / compounding_freq_per_year
    periodic_yield = yield_to_maturity / compounding_freq_per_year
    total_periods = int(n_years * compounding_freq_per_year)

    if total_periods == 0:
        return 0.0

    # Iterate through each period
    for t in range(1, total_periods + 1):
        cash_flow = periodic_coupon_payment
        if t == total_periods:
            cash_flow += face_value # Add face value to the last cash flow

        # Discount factor for bond price (PV of cash flow)
        pv_factor = 1 / ((1 + periodic_yield) ** t)
        
        # Term for Convexity numerator: CF_t * t * (t+1) / (1 + periodic_yield)^(t+2)
        convexity_term_numerator = (cash_flow * t * (t + 1)) / ((1 + periodic_yield) ** (t + 2))
        sum_convexity_numerator_terms += convexity_term_numerator
            
        # Calculate bond price along the way (sum of PV of all cash flows)
        bond_price_denominator += cash_flow * pv_factor

    # --- Handle effectively zero bond price (denominator) ---
    # Define dynamic tolerance based on face_value: 0.05% of face_value, with a minimum of 1e-9.
    # This means if the bond price is less than 0.05% of its face value (or 1e-9, whichever is larger),
    # it is considered effectively zero.
    effectively_zero_threshold = max(face_value * 0.00051, 1e-9) # 0.05% of face value, or min 1e-9

    if math.isclose(bond_price_denominator, 0.0, abs_tol=effectively_zero_threshold):
        raise ValueError("Bond price is effectively zero, convexity is undefined.")
        
    # --- Final Calculation ---
    convexity_raw = sum_convexity_numerator_terms / bond_price_denominator
    
    # Convert convexity from 'periods squared' to 'years squared'
    convexity_in_years_squared = convexity_raw / (compounding_freq_per_year ** 2)
    
    return convexity_in_years_squared


def calculate_forward_rate(spot_rate_t1: float, t1_years: float, spot_rate_t2: float, t2_years: float) -> float:
    """
    Calculates the implied annual effective forward rate between two future points
    on a yield curve, given two spot rates.

    Args:
        spot_rate_t1 (float): The current spot rate (EAR as decimal) for maturity t1. Must be >= -1.
        t1_years (float): The maturity in years for the first spot rate (t1 < t2). Must be positive.
        spot_rate_t2 (float): The current spot rate (EAR as decimal) for maturity t2. Must be >= -1.
        t2_years (float): The maturity in years for the second spot rate (t2 > t1). Must be positive.

    Returns:
        float: The implied annual effective forward rate (as a decimal) from t1 to t2.

    Raises:
        ValueError: If `t1_years` is not less than `t2_years`, or if any rate is less than -1.
                    Or if years are non-positive.
    """
    # --- Input Validations ---
    if t1_years <= 0 or t2_years <= 0:
        raise ValueError("Maturity years (t1_years, t2_years) must be positive.")
    if t1_years >= t2_years:
        raise ValueError("t1_years must be strictly less than t2_years to calculate a forward rate.")
    if spot_rate_t1 < -1 or spot_rate_t2 < -1:
        raise ValueError("Spot rates cannot be less than -1 (or -100%).")
    
    # --- Formula: (1 + R_fwd)^(T2 - T1) = (1 + R_t2)^T2 / (1 + R_t1)^T1 ---
    # R_fwd = [(1 + R_t2)^T2 / (1 + R_t1)^T1]^(1 / (T2 - T1)) - 1
    
    forward_rate = (( (1 + spot_rate_t2)**t2_years ) / ( (1 + spot_rate_t1)**t1_years ))**(1 / (t2_years - t1_years)) - 1
    return forward_rate


def calculate_yield_curve_spot_rate(zero_coupon_bond_price: float, face_value: float, n_years: float) -> float:
    """
    Calculates the spot rate for a given maturity from a zero-coupon bond price.
    Spot rates are the yield to maturity of zero-coupon bonds.

    Args:
        zero_coupon_bond_price (float): The current market price of the zero-coupon bond. Must be positive.
        face_value (float): The face (par) value of the zero-coupon bond. Must be positive.
        n_years (float): The number of years until the bond matures. Must be positive.

    Returns:
        float: The annualized spot rate (as a decimal), compounded annually.

    Raises:
        ValueError: If price, face_value, or n_years are non-positive.
    """
    # --- Input Validations ---
    if zero_coupon_bond_price <= 0:
        raise ValueError("Zero-coupon bond price must be positive.")
    if face_value <= 0:
        raise ValueError("Face value must be positive.")
    if n_years <= 0:
        raise ValueError("Number of years must be positive.")

    # --- Formula: Price = FaceValue / (1 + SpotRate)^n_years ---
    # SpotRate = (FaceValue / Price)^(1 / n_years) - 1
    spot_rate = (face_value / zero_coupon_bond_price)**(1 / n_years) - 1
    return spot_rate

# (Note: bootstrap_yield_curve and calculate_par_rate are complex and less directly related to the current errors.
# They are kept from the previous version with minor reformatting for consistency, but
# a full robust re-implementation of bootstrap would be a project in itself.)

def bootstrap_yield_curve(bond_data: list[dict]) -> dict:
    """
    (CONCEPTUAL OUTLINE / SIMPLIFIED)
    Bootstraps the zero-coupon yield curve from market prices of coupon bonds
    or zero-coupon bonds.

    Args:
        bond_data (list[dict]): A list of dictionaries, where each dictionary
                                represents a bond and contains:
                                - 'maturity_years': float (e.g., 0.5, 1.0, 1.5, ...)
                                - 'coupon_rate': float (annual, as decimal, 0 for zero-coupon)
                                - 'face_value': float
                                - 'market_price': float
                                - 'compounding_freq_per_year': int (e.g., 2 for semi-annual)

    Returns:
        dict: A dictionary mapping maturity (in years) to its bootstrapped zero rate (as a decimal).
              Example: {0.5: 0.01, 1.0: 0.012, 1.5: 0.015}

    Raises:
        ValueError: If input data is malformed or insufficient.
        RuntimeError: If bootstrapping fails to converge or is not possible with the given data.

    Assumptions/Limitations:
    - This is a highly simplified conceptual outline. A robust implementation requires:
        - Precise sorting of bonds by maturity.
        - Iterative numerical methods (e.g., Newton-Raphson) for coupon bonds.
        - Handling of interpolation for non-matching maturities.
    - This version will only handle simple cases where zero rates can be directly derived
      or will provide a placeholder for the iterative process.
    - For simplicity, assumes bonds are sorted by maturity.
    - It's recommended to have zero-coupon bonds or bonds maturing sequentially
      for easier bootstrapping.
    """
    if not bond_data:
        raise ValueError("Bond data cannot be empty.")

    # Sort bonds by maturity
    sorted_bonds = sorted(bond_data, key=lambda b: b['maturity_years'])

    zero_rates = {} # Stores {maturity_year: zero_rate}

    for bond in sorted_bonds:
        maturity = bond['maturity_years']
        coupon_rate = bond['coupon_rate']
        face_value = bond['face_value']
        market_price = bond['market_price']
        compounding_freq = bond['compounding_freq_per_year']

        if maturity in zero_rates:
            continue # Already bootstrapped this maturity or earlier bond

        if compounding_freq <= 0:
            raise ValueError(f"Compounding frequency for bond at {maturity} years must be positive.")
        if market_price <= 0:
            raise ValueError(f"Market price for bond at {maturity} years must be positive.")

        # Handle Zero-Coupon Bonds (simplest case)
        if coupon_rate == 0:
            total_periods = maturity * compounding_freq
            if total_periods == 0:
                raise ValueError(f"Zero maturity for zero-coupon bond at {maturity} years.")
                
            if market_price == 0:
                raise ValueError(f"Market price for zero-coupon bond at {maturity} years cannot be zero.")
                
            try:
                periodic_zero_rate = (face_value / market_price)**(1 / total_periods) - 1
                annual_zero_rate = periodic_zero_rate * compounding_freq
                zero_rates[maturity] = annual_zero_rate
            except Exception as e:
                raise RuntimeError(f"Could not bootstrap zero rate for ZCB at {maturity} years: {e}")
                
        else:
            # Handle Coupon Bonds - This is where iterative solving is usually needed.
            periodic_coupon = (face_value * coupon_rate) / compounding_freq
            total_periods = int(maturity * compounding_freq)
            
            present_value_of_known_cash_flows = 0.0
            
            for i in range(1, total_periods):
                cash_flow_time_in_years = i / compounding_freq
                
                prior_zero_rate_found = False
                for prev_maturity, prev_zero_rate in sorted(zero_rates.items()):
                    if math.isclose(cash_flow_time_in_years, prev_maturity, rel_tol=1e-6):
                        present_value_of_known_cash_flows += periodic_coupon / ((1 + prev_zero_rate / compounding_freq)**i)
                        prior_zero_rate_found = True
                        break
                
                if not prior_zero_rate_found and i > 0 and i < total_periods:
                    raise RuntimeError(f"Cannot bootstrap coupon bond at {maturity} years. Missing exact prior zero rate for period {i}.")

            remaining_price = market_price - present_value_of_known_cash_flows
            final_cash_flow = periodic_coupon + face_value
            
            if remaining_price <= 0:
                raise RuntimeError(f"Remaining price for coupon bond at {maturity} years is non-positive after discounting prior cash flows, cannot solve for final zero rate.")
                
            try:
                term = (final_cash_flow / remaining_price)**(1 / total_periods)
                periodic_zero_rate = term - 1
                annual_zero_rate = periodic_zero_rate * compounding_freq
                zero_rates[maturity] = annual_zero_rate
            except Exception as e:
                raise RuntimeError(f"Could not bootstrap final zero rate for coupon bond at {maturity} years: {e}")
                
    return zero_rates


def calculate_par_rate(spot_rates: list[float], maturities: list[float]) -> float:
    """
    Calculates the par yield for a bond given a set of spot rates for various maturities.
    The par yield is the coupon rate that makes a bond's price equal to its face value.

    Args:
        spot_rates (list[float]): A list of annualized spot rates (as decimals) corresponding to each maturity.
                                  Rates must be non-negative.
        maturities (list[float]): A list of maturities (in years) corresponding to each spot rate.
                                   Must be positive and increasing.
                                   Assumes sorted maturities and corresponding spot rates.

    Returns:
        float: The annualized par rate (as a decimal).

    Raises:
        ValueError: If lists are empty, have mismatched lengths, or if maturities are not positive and increasing.
                    Or if spot rates are less than -1.
    
    Assumptions/Limitations:
    - Assumes a bond with a face value of 1 (or any face value, as it cancels out in the ratio).
    - Assumes annual coupon payments for simplicity. For semi-annual, adjust logic.
    - Maturities are assumed to be 1, 2, ..., N for a standard par yield calculation,
      where the last maturity in the list is the bond's maturity.
    """
    if not spot_rates or not maturities:
        raise ValueError("Spot rates and maturities lists cannot be empty.")
    if len(spot_rates) != len(maturities):
        raise ValueError("Spot rates and maturities lists must have the same length.")
    
    for i, m in enumerate(maturities):
        if m <= 0:
            raise ValueError("Maturities must be positive.")
        if i > 0 and m <= maturities[i-1]:
            raise ValueError("Maturities must be strictly increasing.")
    
    for sr in spot_rates:
        if sr < -1:
            raise ValueError("Spot rates cannot be less than -1 (or -100%).")

    sum_discount_factors = 0
    for i, m in enumerate(maturities):
        discount_factor = 1 / ((1 + spot_rates[i])**m)
        sum_discount_factors += discount_factor
    
    last_spot_rate = spot_rates[-1]
    last_maturity = maturities[-1]
    
    pv_of_face_value = 1 / ((1 + last_spot_rate)**last_maturity)

    numerator = 1 - pv_of_face_value
    denominator = sum_discount_factors

    if math.isclose(denominator, 0.0, abs_tol=1e-9): # Use abs_tol for denominator
        raise ValueError("Cannot calculate par rate: sum of discount factors is zero or effectively zero.")

    par_rate = numerator / denominator
    return par_rate