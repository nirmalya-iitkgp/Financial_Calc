# financial_calculator/gui/fixed_income_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Union

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import Fixed Income mathematical functions as per PROJECT_STRUCTURE.md
# From bonds.py
from mathematical_functions.bonds import (
    calculate_bond_price,
    calculate_zero_coupon_bond_price,
    calculate_zero_coupon_bond_yield
)
# From bond_risk.py (Note: _calculate_macaulay_duration_helper is for internal use within math functions)
from mathematical_functions.bond_risk import (
    calculate_modified_duration,
    calculate_convexity as calculate_bond_risk_convexity # Alias to avoid name conflict if both are imported
)
# From fixed_income_advanced.py (These versions are preferred for GUI as they are higher-level)
from mathematical_functions.fixed_income_advanced import (
    calculate_macaulay_duration, # This is the main one for GUI use
    calculate_convexity,         # This is the main one for GUI use
    calculate_forward_rate,      # Yield curve specific
    calculate_yield_curve_spot_rate,
    bootstrap_yield_curve,       # Complex input
    calculate_par_rate           # Complex input
)

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class FixedIncomeGUI(BaseGUI):
    """
    GUI module for Fixed Income (Bonds) calculations.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        
        self.solve_for_var = tk.StringVar(value="COUPON_BOND_PRICE") # Default calculation

        self._create_fixed_income_widgets(self.scrollable_frame)
        self._update_input_fields_state() # Initial state update

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate Fixed Income", command=self.calculate_fixed_income)
        logger.info("FixedIncomeGUI initialized.")

    def _create_fixed_income_widgets(self, parent_frame):
        """
        Creates the specific input fields and 'Solve For' options for Fixed Income calculations.
        """
        fixed_income_inputs_frame = ttk.LabelFrame(parent_frame, text="Fixed Income Inputs")
        fixed_income_inputs_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        fixed_income_inputs_frame.grid_columnconfigure(1, weight=1) # Allow input entries to expand

        # Core Bond Inputs
        self.create_input_row(fixed_income_inputs_frame, 0, "Face Value:", "1000.00", "The par value of the bond.")
        self.create_input_row(fixed_income_inputs_frame, 1, "Coupon Rate (Annual %):", "5.00", "Annual coupon rate as a percentage (e.g., 5 for 5%).")
        self.create_input_row(fixed_income_inputs_frame, 2, "Yield to Maturity (Annual %):", "6.00", "Required annual rate of return as a percentage (YTM).")
        self.create_input_row(fixed_income_inputs_frame, 3, "Years to Maturity:", "10.00", "Number of years until the bond matures.")
        self.create_input_row(fixed_income_inputs_frame, 4, "Compounding Freq. (per year):", "2", "Number of times interest is compounded per year (e.g., 2 for semi-annual).")
        self.create_input_row(fixed_income_inputs_frame, 5, "Current Price (for Yield):", "950.00", "Current market price of the bond (used when calculating yield).")

        # Inputs for Forward/Spot Rates (simplified for single calculations)
        self.create_input_row(fixed_income_inputs_frame, 6, "Spot Rate T1 (Annual %):", "1.00", "Spot rate for period T1 (for forward rate calculation).")
        self.create_input_row(fixed_income_inputs_frame, 7, "Years T1:", "1.00", "Years for spot rate T1.")
        self.create_input_row(fixed_income_inputs_frame, 8, "Spot Rate T2 (Annual %):", "2.00", "Spot rate for period T2 (for forward rate calculation).")
        self.create_input_row(fixed_income_inputs_frame, 9, "Years T2:", "2.00", "Years for spot rate T2.")
        
        # --- Solve For Section ---
        solve_for_frame = ttk.LabelFrame(parent_frame, text="Calculate")
        solve_for_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        solve_for_frame.grid_columnconfigure(0, weight=1)

        solve_options = {
            "Coupon Bond Price": "COUPON_BOND_PRICE",
            "Zero-Coupon Bond Price": "ZERO_COUPON_BOND_PRICE",
            "Zero-Coupon Bond Yield": "ZERO_COUPON_BOND_YIELD",
            "Macaulay Duration": "MACAULAY_DURATION",
            "Modified Duration": "MODIFIED_DURATION",
            "Convexity": "CONVEXITY",
            "Forward Rate (Yield Curve)": "FORWARD_RATE_YC",
            "Spot Rate (from ZC Bond)": "SPOT_RATE_ZC",
        }

        row_num = 0
        for text, value in solve_options.items():
            rb = ttk.Radiobutton(solve_for_frame, text=text, variable=self.solve_for_var,
                                 value=value, command=self._update_input_fields_state)
            rb.grid(row=row_num // 2, column=row_num % 2, sticky="w", padx=5, pady=2)
            row_num += 1
        
        # Adjust common buttons and result frame positions
        self.common_buttons_frame.grid(row=2, column=0, columnspan=1, pady=5)
        self.result_frame.grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

    def _update_input_fields_state(self):
        """
        Enables/disables input fields based on the selected 'Solve For' option.
        """
        selected_option = self.solve_for_var.get()

        # All fields defined by create_input_row using their generated keys
        all_field_keys = [
            "face_value", "coupon_rate_annual", "yield_to_maturity_annual",
            "years_to_maturity", "compounding_freq_per_year",
            "current_price_for_yield",
            "spot_rate_t1_annual", "years_t1", "spot_rate_t2_annual", "years_t2"
        ]

        # Enable all fields first
        for key in all_field_keys:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")
            else:
                logger.warning(f"Field key '{key}' not found in input_fields during state update in FixedIncomeGUI.")
        
        # Then disable specific fields based on selected_option
        if selected_option == "COUPON_BOND_PRICE":
            self.input_fields["current_price_for_yield"].config(state="disabled")
            self.input_fields["spot_rate_t1_annual"].config(state="disabled")
            self.input_fields["years_t1"].config(state="disabled")
            self.input_fields["spot_rate_t2_annual"].config(state="disabled")
            self.input_fields["years_t2"].config(state="disabled")
        elif selected_option == "ZERO_COUPON_BOND_PRICE":
            self.input_fields["coupon_rate_annual"].config(state="disabled")
            self.input_fields["current_price_for_yield"].config(state="disabled")
            self.input_fields["spot_rate_t1_annual"].config(state="disabled")
            self.input_fields["years_t1"].config(state="disabled")
            self.input_fields["spot_rate_t2_annual"].config(state="disabled")
            self.input_fields["years_t2"].config(state="disabled")
        elif selected_option == "ZERO_COUPON_BOND_YIELD":
            self.input_fields["coupon_rate_annual"].config(state="disabled")
            self.input_fields["yield_to_maturity_annual"].config(state="disabled")
            self.input_fields["spot_rate_t1_annual"].config(state="disabled")
            self.input_fields["years_t1"].config(state="disabled")
            self.input_fields["spot_rate_t2_annual"].config(state="disabled")
            self.input_fields["years_t2"].config(state="disabled")
        elif selected_option in ["MACAULAY_DURATION", "MODIFIED_DURATION", "CONVEXITY"]:
            self.input_fields["current_price_for_yield"].config(state="disabled")
            self.input_fields["spot_rate_t1_annual"].config(state="disabled")
            self.input_fields["years_t1"].config(state="disabled")
            self.input_fields["spot_rate_t2_annual"].config(state="disabled")
            self.input_fields["years_t2"].config(state="disabled")
        elif selected_option == "FORWARD_RATE_YC":
            self.input_fields["face_value"].config(state="disabled")
            self.input_fields["coupon_rate_annual"].config(state="disabled")
            self.input_fields["yield_to_maturity_annual"].config(state="disabled")
            self.input_fields["years_to_maturity"].config(state="disabled")
            self.input_fields["compounding_freq_per_year"].config(state="disabled")
            self.input_fields["current_price_for_yield"].config(state="disabled")
        elif selected_option == "SPOT_RATE_ZC":
            self.input_fields["coupon_rate_annual"].config(state="disabled")
            self.input_fields["yield_to_maturity_annual"].config(state="disabled")
            self.input_fields["spot_rate_t1_annual"].config(state="disabled")
            self.input_fields["years_t1"].config(state="disabled")
            self.input_fields["spot_rate_t2_annual"].config(state="disabled")
            self.input_fields["years_t2"].config(state="disabled")

    def calculate_fixed_income(self):
        """
        Performs the Fixed Income calculation based on user inputs and the selected option.
        """
        self.display_result("Calculating...", is_error=False)
        solve_for = self.solve_for_var.get()

        # --- Get and Validate Inputs ---
        # Note: All rates are assumed to be percentages (e.g., "5" for 5%) from GUI.
        # They will be converted to decimals (e.g., 0.05) for math functions.

        face_value_str = self.get_input_value("face_value")
        coupon_rate_str = self.get_input_value("coupon_rate_annual")
        ym_str = self.get_input_value("yield_to_maturity_annual")
        years_str = self.get_input_value("years_to_maturity")
        comp_freq_str = self.get_input_value("compounding_freq_per_year") # Corrected key
        current_price_str = self.get_input_value("current_price_for_yield")

        # Yield curve specific inputs
        spot_rate_t1_str = self.get_input_value("spot_rate_t1_annual") # Corrected key
        years_t1_str = self.get_input_value("years_t1")
        spot_rate_t2_str = self.get_input_value("spot_rate_t2_annual") # Corrected key
        years_t2_str = self.get_input_value("years_t2")
        
        # --- Common Validation & Conversion ---
        # Initialize variables
        fv, cr, ytm, n_years, comp_freq, current_price = 0.0, 0.0, 0.0, 0.0, 1.0, 0.0
        sr_t1, t1, sr_t2, t2 = 0.0, 0.0, 0.0, 0.0

        try:
            if solve_for in ["COUPON_BOND_PRICE", "ZERO_COUPON_BOND_PRICE", "MACAULAY_DURATION", "MODIFIED_DURATION", "CONVEXITY"]:
                is_valid, fv = self.validate_input(face_value_str, 'positive_numeric', "Face Value")
                if not is_valid: return self.display_result(fv, is_error=True)
                
                is_valid, ytm = self.validate_input(ym_str, 'numeric', "Yield to Maturity")
                if not is_valid: return self.display_result(ytm, is_error=True)
                ytm /= 100.0 # Convert to decimal

                is_valid, n_years = self.validate_input(years_str, 'positive_numeric', "Years to Maturity")
                if not is_valid: return self.display_result(n_years, is_error=True)
                
                is_valid, comp_freq = self.validate_input(comp_freq_str, 'positive_integer', "Compounding Frequency")
                if not is_valid: return self.display_result(comp_freq, is_error=True)
                
                if solve_for == "COUPON_BOND_PRICE" or solve_for in ["MACAULAY_DURATION", "MODIFIED_DURATION", "CONVEXITY"]:
                    is_valid, cr = self.validate_input(coupon_rate_str, 'numeric', "Coupon Rate")
                    if not is_valid: return self.display_result(cr, is_error=True)
                    cr /= 100.0 # Convert to decimal
            
            elif solve_for == "ZERO_COUPON_BOND_YIELD":
                is_valid, fv = self.validate_input(face_value_str, 'positive_numeric', "Face Value")
                if not is_valid: return self.display_result(fv, is_error=True)
                
                is_valid, current_price = self.validate_input(current_price_str, 'positive_numeric', "Current Price")
                if not is_valid: return self.display_result(current_price, is_error=True)
                
                is_valid, n_years = self.validate_input(years_str, 'positive_numeric', "Years to Maturity")
                if not is_valid: return self.display_result(n_years, is_error=True)
                
                is_valid, comp_freq = self.validate_input(comp_freq_str, 'positive_integer', "Compounding Frequency")
                if not is_valid: return self.display_result(comp_freq, is_error=True)
            
            elif solve_for == "FORWARD_RATE_YC":
                is_valid, sr_t1 = self.validate_input(spot_rate_t1_str, 'numeric', "Spot Rate T1")
                if not is_valid: return self.display_result(sr_t1, is_error=True)
                sr_t1 /= 100.0 # Convert to decimal
                
                is_valid, t1 = self.validate_input(years_t1_str, 'positive_numeric', "Years T1")
                if not is_valid: return self.display_result(t1, is_error=True)
                
                is_valid, sr_t2 = self.validate_input(spot_rate_t2_str, 'numeric', "Spot Rate T2")
                if not is_valid: return self.display_result(sr_t2, is_error=True)
                sr_t2 /= 100.0 # Convert to decimal
                
                is_valid, t2 = self.validate_input(years_t2_str, 'positive_numeric', "Years T2")
                if not is_valid: return self.display_result(t2, is_error=True)

                if t1 >= t2:
                    self.display_result("Years T2 must be greater than Years T1 for Forward Rate calculation.", is_error=True)
                    return
            
            elif solve_for == "SPOT_RATE_ZC":
                is_valid, current_price = self.validate_input(current_price_str, 'positive_numeric', "Current Price")
                if not is_valid: return self.display_result(current_price, is_error=True)
                
                is_valid, fv = self.validate_input(face_value_str, 'positive_numeric', "Face Value")
                if not is_valid: return self.display_result(fv, is_error=True)
                
                is_valid, n_years = self.validate_input(years_str, 'positive_numeric', "Years to Maturity")
                if not is_valid: return self.display_result(n_years, is_error=True)


            # --- Perform Calculation ---
            result = None
            if solve_for == "COUPON_BOND_PRICE":
                result = calculate_bond_price(fv, cr, ytm, n_years, comp_freq)
                self.display_result(f"Coupon Bond Price: {self.format_currency_output(result)}")
            elif solve_for == "ZERO_COUPON_BOND_PRICE":
                result = calculate_zero_coupon_bond_price(fv, ytm, n_years, comp_freq)
                self.display_result(f"Zero-Coupon Bond Price: {self.format_currency_output(result)}")
            elif solve_for == "ZERO_COUPON_BOND_YIELD":
                result_decimal = calculate_zero_coupon_bond_yield(fv, current_price, n_years, comp_freq)
                self.display_result(f"Zero-Coupon Bond Yield: {self.format_percentage_output(result_decimal)}")
            elif solve_for == "MACAULAY_DURATION":
                # Ensure the correct Macaulay duration is called (from fixed_income_advanced.py)
                result = calculate_macaulay_duration(fv, cr, ytm, n_years, comp_freq)
                self.display_result(f"Macaulay Duration: {self.format_number_output(result, 4)} periods")
            elif solve_for == "MODIFIED_DURATION":
                # Ensure the correct Modified duration is called (from bond_risk.py or fixed_income_advanced.py - both have it. Using bond_risk for variety)
                # Note: If `calculate_macaulay_duration` is needed internally by `calculate_modified_duration`,
                # ensure `bond_risk.py` or the aliased `_calculate_macaulay_duration_helper` is correctly structured.
                # For now, assuming direct call.
                result = calculate_modified_duration(fv, cr, ytm, n_years, comp_freq)
                self.display_result(f"Modified Duration: {self.format_number_output(result, 4)}")
            elif solve_for == "CONVEXITY":
                # Using the Convexity from fixed_income_advanced.py
                result = calculate_convexity(fv, cr, ytm, n_years, comp_freq)
                self.display_result(f"Convexity: {self.format_number_output(result, 6)}")
            elif solve_for == "FORWARD_RATE_YC":
                result_decimal = calculate_forward_rate(sr_t1, t1, sr_t2, t2)
                self.display_result(f"Implied Forward Rate: {self.format_percentage_output(result_decimal)}")
            elif solve_for == "SPOT_RATE_ZC":
                result_decimal = calculate_yield_curve_spot_rate(current_price, fv, n_years)
                self.display_result(f"Calculated Spot Rate (from ZCB): {self.format_percentage_output(result_decimal)}")

        except ValueError as e:
            logger.error(f"Fixed Income Calculation Error (ValueError): {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Fixed Income Calculation Error (ZeroDivisionError): {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs like rate or frequency.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Fixed Income calculation: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the solve_for_var and update state.
        """
        super().clear_inputs()
        self.solve_for_var.set("COUPON_BOND_PRICE") # Reset to default
        self._update_input_fields_state() # Update UI based on reset

# Example usage (for testing FixedIncomeGUI in isolation if desired)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fixed Income Calculator")
    root.geometry("900x700")

    # style = ttk.Style()
    # style.theme_use('clam')

    fixed_income_frame = FixedIncomeGUI(root)
    fixed_income_frame.pack(fill="both", expand=True)

    root.mainloop()