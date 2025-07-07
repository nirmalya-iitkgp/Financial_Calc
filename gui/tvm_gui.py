# financial_calculator/gui/tvm_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import TVM mathematical functions
from mathematical_functions.tvm import (
    calculate_fv_single_sum,
    calculate_pv_single_sum,
    calculate_fv_ordinary_annuity,
    calculate_pv_ordinary_annuity,
    calculate_loan_payment,
    convert_apr_to_ear
)

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TVMGUI(BaseGUI):
    """
    GUI module for Time Value of Money (TVM) calculations.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.tvm_inputs_frame = None

        # Variable to hold the selected TVM variable to solve for
        self.solve_for_var = tk.StringVar(value="FV") # Default to solving for Future Value

        self._create_tvm_widgets(self.scrollable_frame) # Place TVM-specific widgets in scrollable frame
        self._update_input_fields_state() # Initial state update

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate TVM", command=self.calculate_tvm)
        logger.info("TVMGUI initialized.")

    def _create_tvm_widgets(self, parent_frame):
        """
        Creates the specific input fields and 'Solve For' options for TVM calculations.
        """
        self.tvm_inputs_frame = ttk.LabelFrame(parent_frame, text="Time Value of Money Inputs")
        self.tvm_inputs_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.tvm_inputs_frame.grid_columnconfigure(1, weight=1) # Allow input entries to expand

        # Row 0: Present Value
        self.create_input_row(self.tvm_inputs_frame, 0, "Present Value (PV):", "0.00", "The current value of a future sum of money or stream of cash flows.")
        # Row 1: Future Value
        self.create_input_row(self.tvm_inputs_frame, 1, "Future Value (FV):", "0.00", "The value of a current asset at a future date based on an assumed rate of growth.")
        # Row 2: Payment (PMT)
        self.create_input_row(self.tvm_inputs_frame, 2, "Payment (PMT):", "0.00", "The amount of each periodic payment in an annuity or loan.")
        # Row 3: Interest Rate (Annual %): Note the actual label in BaseGUI determines the key
        self.create_input_row(self.tvm_inputs_frame, 3, "Interest Rate (Annual %):", "5.00", "The annual interest rate. Enter as a percentage (e.g., 5 for 5%).")
        # Row 4: Number of Periods (N)
        self.create_input_row(self.tvm_inputs_frame, 4, "Number of Periods (N):", "1.00", "The total number of compounding periods or payments.")
        # Row 5: Compounding Frequency per Year
        self.create_input_row(self.tvm_inputs_frame, 5, "Compounding Freq. (per year):", "12", "How many times interest is compounded per year (e.g., 1 for annual, 12 for monthly).")
        # Row 6: Loan Principal (for Loan Payment specific calculation)
        self.create_input_row(self.tvm_inputs_frame, 6, "Loan Principal (for PMT):", "0.00", "The initial amount of the loan, used specifically for loan payment calculation.")
        # Row 7: Number of Years (for Loan Payment specific calculation)
        self.create_input_row(self.tvm_inputs_frame, 7, "Number of Years (for PMT):", "0.00", "The total duration of the loan in years, used specifically for loan payment calculation.")


        # --- Solve For Section ---
        solve_for_frame = ttk.LabelFrame(parent_frame, text="Solve For")
        solve_for_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        solve_for_frame.grid_columnconfigure(0, weight=1) # Center radio buttons

        solve_options = {
            "Future Value (FV)": "FV",
            "Present Value (PV)": "PV",
            "Loan Payment (PMT)": "LOAN_PMT",
            "Effective Annual Rate (EAR)": "EAR"
        }

        row_num = 0
        for text, value in solve_options.items():
            rb = ttk.Radiobutton(solve_for_frame, text=text, variable=self.solve_for_var,
                                 value=value, command=self._update_input_fields_state)
            rb.grid(row=row_num // 2, column=row_num % 2, sticky="w", padx=5, pady=2)
            row_num += 1

        # Place the common buttons frame below the TVM inputs and Solve For sections
        # Adjust row for common buttons (which is row 100 in BaseGUI)
        self.common_buttons_frame.grid(row=2, column=0, columnspan=1, pady=5)
        self.result_frame.grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky="ew") # Adjust result frame position

    def _update_input_fields_state(self):
        """
        Enables/disables input fields based on the selected 'Solve For' option.
        """
        selected_option = self.solve_for_var.get()

        # Define the CORRECT keys as they are now generated by BaseGUI.create_input_row
        FIELD_KEYS = {
            "pv": "present_value_pv",
            "fv": "future_value_fv",
            "pmt": "payment_pmt",
            "rate": "interest_rate_annual", # Matches "Interest Rate (Annual %):" -> "interest_rate_annual"
            "n": "number_of_periods_n",
            "comp_freq": "compounding_freq_per_year", # Matches "Compounding Freq. (per year):" -> "compounding_freq_per_year"
            "loan_principal": "loan_principal_for_pmt", # Matches "Loan Principal (for PMT):" -> "loan_principal_for_pmt"
            "loan_years": "number_of_years_for_pmt", # Matches "Number of Years (for PMT):" -> "number_of_years_for_pmt"
        }

        # Enable all relevant fields first
        for key_alias in FIELD_KEYS.values():
            if key_alias in self.input_fields:
                self.input_fields[key_alias].config(state="normal")
            else:
                logger.warning(f"Field key '{key_alias}' not found in input_fields during state update in TVMGUI.")
        
        # Disable the field corresponding to the selected "Solve For" option
        if selected_option == "FV":
            self.input_fields[FIELD_KEYS["fv"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_principal"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_years"]].config(state="disabled")
        elif selected_option == "PV":
            self.input_fields[FIELD_KEYS["pv"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_principal"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_years"]].config(state="disabled")
        elif selected_option == "LOAN_PMT":
            self.input_fields[FIELD_KEYS["pmt"]].config(state="disabled") # PMT is what we solve for
            # Ensure other specific loan inputs are enabled
            self.input_fields[FIELD_KEYS["pv"]].config(state="disabled") # PV is not used for loan payment
            self.input_fields[FIELD_KEYS["fv"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["n"]].config(state="disabled") # N_periods is not used for loan payment
            self.input_fields[FIELD_KEYS["loan_principal"]].config(state="normal")
            self.input_fields[FIELD_KEYS["loan_years"]].config(state="normal")
        elif selected_option == "EAR":
            #self.input_fields[FIELD_KEYS["rate"]].config(state="disabled") # We output EAR
            self.input_fields[FIELD_KEYS["pv"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["fv"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["pmt"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["n"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_principal"]].config(state="disabled")
            self.input_fields[FIELD_KEYS["loan_years"]].config(state="disabled")


    def calculate_tvm(self):
        """
        Performs the TVM calculation based on user inputs and the selected 'Solve For' option.
        """
        self.display_result("Calculating...", is_error=False) # Clear previous messages

        solve_for = self.solve_for_var.get()
        
        # Define the CORRECT keys for retrieval
        FIELD_KEYS = {
            "pv": "present_value_pv",
            "fv": "future_value_fv",
            "pmt": "payment_pmt",
            "rate": "interest_rate_annual",
            "n": "number_of_periods_n",
            "comp_freq": "compounding_freq_per_year",
            "loan_principal": "loan_principal_for_pmt",
            "loan_years": "number_of_years_for_pmt",
        }

        pv_str = self.get_input_value(FIELD_KEYS["pv"])
        fv_str = self.get_input_value(FIELD_KEYS["fv"])
        pmt_str = self.get_input_value(FIELD_KEYS["pmt"])
        rate_str = self.get_input_value(FIELD_KEYS["rate"])
        n_str = self.get_input_value(FIELD_KEYS["n"])
        comp_freq_str = self.get_input_value(FIELD_KEYS["comp_freq"])
        loan_principal_str = self.get_input_value(FIELD_KEYS["loan_principal"])
        loan_years_str = self.get_input_value(FIELD_KEYS["loan_years"])

        # Validate general numeric inputs - validations dictionary not strictly needed here but kept for context
        # validations = {
        #     "PV": self.validate_input(pv_str, 'numeric', "Present Value"),
        #     "FV": self.validate_input(fv_str, 'numeric', "Future Value"),
        #     "PMT": self.validate_input(pmt_str, 'numeric', "Payment"),
        #     "Rate": self.validate_input(rate_str, 'numeric', "Interest Rate"),
        #     "N": self.validate_input(n_str, 'positive_numeric', "Number of Periods"),
        #     "Compounding Freq": self.validate_input(comp_freq_str, 'positive_numeric', "Compounding Frequency"),
        #     "Loan Principal": self.validate_input(loan_principal_str, 'positive_numeric', "Loan Principal"),
        #     "Loan Years": self.validate_input(loan_years_str, 'positive_numeric', "Number of Years")
        # }

        # Initialize variables to None or 0.0
        pv, fv, pmt, rate, n, comp_freq, loan_principal, loan_years = 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0
        
        # Determine which variables are required based on solve_for type
        required_fields = []
        if solve_for in ["FV", "PV"]:
            # Only include fields that are *not* being solved for as required
            if solve_for != "PV": required_fields.append(("PV", pv_str, 'numeric', "Present Value"))
            if solve_for != "FV": required_fields.append(("FV", fv_str, 'numeric', "Future Value"))
            if solve_for != "PMT": required_fields.append(("PMT", pmt_str, 'numeric', "Payment"))
            if solve_for != "RATE": required_fields.append(("Rate", rate_str, 'numeric', "Interest Rate"))
            if solve_for != "N": required_fields.append(("N", n_str, 'positive_numeric', "Number of Periods"))
            required_fields.append(("Compounding Freq", comp_freq_str, 'positive_numeric', "Compounding Frequency"))
        elif solve_for == "LOAN_PMT":
            required_fields.append(("Loan Principal", loan_principal_str, 'positive_numeric', "Loan Principal"))
            required_fields.append(("Rate", rate_str, 'numeric', "Annual Rate")) # Use generic 'Rate' for loan rate
            required_fields.append(("Loan Years", loan_years_str, 'positive_numeric', "Number of Years"))
            required_fields.append(("Compounding Freq", comp_freq_str, 'positive_numeric', "Compounding Frequency"))
        elif solve_for == "EAR":
            required_fields.append(("Rate", rate_str, 'numeric', "Annual Percentage Rate (APR)"))
            required_fields.append(("Compounding Freq", comp_freq_str, 'positive_integer', "Compounding Frequency"))

        # Perform specific required field validation and conversion
        for field_name_key, val_str, val_type, display_name in required_fields:
            is_valid, converted_val = self.validate_input(val_str, val_type, display_name)
            if not is_valid:
                self.display_result(converted_val, is_error=True)
                return

            if field_name_key == "PV": pv = converted_val
            elif field_name_key == "FV": fv = converted_val
            elif field_name_key == "PMT": pmt = converted_val
            elif field_name_key == "Rate": rate = converted_val / 100.0 # Convert percentage to decimal
            elif field_name_key == "N": n = converted_val
            elif field_name_key == "Compounding Freq": comp_freq = converted_val
            elif field_name_key == "Loan Principal": loan_principal = converted_val
            elif field_name_key == "Loan Years": loan_years = converted_val
            
        # Specific checks for combinations
        if solve_for in ["FV", "PV"]:
            # If solving for FV/PV when PMT is 0, it's a single sum calculation.
            # If PMT is non-zero, it's an ordinary annuity.
            # No additional combination validation needed here for now as the logic within try-except handles it.
            pass

        try:
            result = None
            if solve_for == "FV":
                # If PMT is 0, calculate FV of single sum
                if pmt == 0:
                    # If PV is also 0, and N or Rate is not 0, this might be an invalid scenario for single sum FV
                    if pv == 0 and (n != 0 or rate != 0):
                        self.display_result("For Future Value (Single Sum) calculation, if Payment (PMT) is zero, Present Value (PV) must be non-zero.", is_error=True)
                        return
                    result = calculate_fv_single_sum(pv, rate, n * comp_freq)
                    result_msg = f"Future Value (Single Sum): {self.format_currency_output(result)}"
                else:
                    # For FV of ordinary annuity, PV is typically 0 if it's purely annuity based.
                    # If PV is also non-zero, it implies a combination of single sum and annuity,
                    # which our current `calculate_fv_ordinary_annuity` doesn't directly handle.
                    # For simplicity, if PMT is non-zero, we'll calculate annuity FV.
                    # A more robust solution might require summing results of separate calculations.
                    result = calculate_fv_ordinary_annuity(pmt, rate, n * comp_freq)
                    result_msg = f"Future Value (Ordinary Annuity): {self.format_currency_output(result)}"

            elif solve_for == "PV":
                # If PMT is 0, calculate PV of single sum
                if pmt == 0:
                    if fv == 0 and (n != 0 or rate != 0):
                        self.display_result("For Present Value (Single Sum) calculation, if Payment (PMT) is zero, Future Value (FV) must be non-zero.", is_error=True)
                        return
                    result = calculate_pv_single_sum(fv, rate, n * comp_freq)
                    result_msg = f"Present Value (Single Sum): {self.format_currency_output(result)}"
                else:
                    # Similar to FV, if PMT is non-zero, prioritize annuity PV.
                    result = calculate_pv_ordinary_annuity(pmt, rate, n * comp_freq)
                    result_msg = f"Present Value (Ordinary Annuity): {self.format_currency_output(result)}"

            elif solve_for == "LOAN_PMT":
                # Special handling for loan payment
                if loan_principal <= 0:
                    self.display_result("Loan Principal must be positive for Loan Payment calculation.", is_error=True)
                    return
                # Annual Rate `rate` is already converted to decimal (e.g., 0.05 for 5%)
                if rate <= 0: # Note: Real rates can be 0 or negative, but for typical loan PMT, positive rate is expected
                    self.display_result("Annual Rate must be positive for Loan Payment calculation.", is_error=True)
                    return
                if loan_years <= 0:
                    self.display_result("Number of Years must be positive for Loan Payment calculation.", is_error=True)
                    return

                result = calculate_loan_payment(loan_principal, rate, loan_years, comp_freq)
                result_msg = f"Loan Payment (PMT): {self.format_currency_output(result)}"

            
            elif solve_for == "EAR":
                # APR is already divided by 100 in input parsing, so `rate` is a decimal (e.g., 0.05)
                if rate <= 0: # Note: APR can be 0, but for EAR calculation, a positive rate is typically expected
                    self.display_result("Annual Percentage Rate (APR) must be positive for EAR calculation.", is_error=True)
                    return
                if comp_freq <= 0:
                    self.display_result("Compounding Frequency must be positive for EAR calculation.", is_error=True)
                    return
                result = convert_apr_to_ear(rate, comp_freq)
                result_msg = f"Effective Annual Rate (EAR): {self.format_percentage_output(result)}"

            if result is not None:
                self.display_result(result_msg)
            else:
                self.display_result("Unable to calculate. Check inputs and selected 'Solve For' option.", is_error=True)

        except ValueError as e:
            logger.error(f"TVM Calculation Error (ValueError): {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"TVM Calculation Error (ZeroDivisionError): {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs like rate or periods.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during TVM calculation: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the solve_for_var.
        """
        super().clear_inputs()
        self.solve_for_var.set("FV") # Reset to default
        self._update_input_fields_state() # Update UI based on reset

# Example usage (for testing TVMGUI in isolation if desired)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("TVM Calculator")
    root.geometry("800x600")

    # style = ttk.Style()
    # style.theme_use('clam')

    tvm_frame = TVMGUI(root)
    tvm_frame.pack(fill="both", expand=True)

    root.mainloop()