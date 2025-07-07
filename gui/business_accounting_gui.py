# financial_calculator/gui/business_accounting_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import math
from typing import Union, List, Dict, Any
import re # Needed for field key generation consistency

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import mathematical functions as per PROJECT_STRUCTURE.md
# From capital_budgeting.py (canonical source for NPV/IRR for this GUI)
from mathematical_functions.capital_budgeting import (
    calculate_payback_period,
    calculate_discounted_payback_period,
    calculate_npv,
    calculate_irr,
    calculate_profitability_index
)
# From banking_risk.py
from mathematical_functions.banking_risk import (
    calculate_expected_loss,
    calculate_asset_liability_gap
)
# From accounting.py
from mathematical_functions.accounting import (
    calculate_depreciation_straight_line,
    calculate_depreciation_double_declining_balance
)

# Import constants (for formatting, if needed in the future directly)
from config import DEFAULT_WINDOW_WIDTH # for example usage

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BusinessAccountingGUI(BaseGUI):
    """
    GUI module for Business and Accounting related calculations, including
    Capital Budgeting, Banking Risk, and Depreciation.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Business & Accounting Models", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Center the title
        self.scrollable_frame.grid_columnconfigure(1, weight=1) # Span across 2 columns

        # Variables for model selection (replaces solve_for_var radiobuttons)
        self.selected_model_var = tk.StringVar(value="Select a Model")

        # Dictionary to hold frames for each model's inputs
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}
        # Dictionary to store the specific input field keys for each model
        self.model_field_keys: Dict[str, List[str]] = {}

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        self._create_all_model_input_widgets(start_row=2) # Start below model selection

        self._hide_all_input_frames() # Hide all initially

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate Model", command=self.calculate_selected_model)
        logger.info("BusinessAccountingGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Net Present Value (NPV)",
            "Internal Rate of Return (IRR)",
            "Payback Period",
            "Discounted Payback Period",
            "Profitability Index (PI)",
            "Expected Loss (EL)",
            "Asset-Liability Gap",
            "Straight-Line Depreciation",
            "Double-Declining Balance Depreciation",
        ]
        self.model_combobox = ttk.Combobox(
            model_select_frame,
            textvariable=self.selected_model_var,
            values=self.model_options,
            state="readonly"
        )
        self.model_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)

    def _create_all_model_input_widgets(self, start_row: int):
        """
        Creates all input fields and frames for each model supported by this GUI,
        but keeps them hidden initially.
        """
        parent_for_models = self.scrollable_frame

        # Capital Budgeting Models (group together for shared inputs)
        self.model_input_frames["Net Present Value (NPV)"] = self._create_capital_budgeting_widgets(parent_for_models, "Capital Budgeting Inputs")
        self.model_input_frames["Net Present Value (NPV)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.model_input_frames["Internal Rate of Return (IRR)"] = self.model_input_frames["Net Present Value (NPV)"] # Same frame
        self.model_input_frames["Payback Period"] = self.model_input_frames["Net Present Value (NPV)"] # Same frame
        self.model_input_frames["Discounted Payback Period"] = self.model_input_frames["Net Present Value (NPV)"] # Same frame
        self.model_input_frames["Profitability Index (PI)"] = self.model_input_frames["Net Present Value (NPV)"] # Same frame

        # Banking Risk Models
        self.model_input_frames["Expected Loss (EL)"] = self._create_banking_risk_widgets(parent_for_models, "Banking Risk Inputs")
        self.model_input_frames["Expected Loss (EL)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.model_input_frames["Asset-Liability Gap"] = self.model_input_frames["Expected Loss (EL)"] # Same frame

        # Accounting (Depreciation) Models
        self.model_input_frames["Straight-Line Depreciation"] = self._create_depreciation_widgets(parent_for_models, "Accounting (Depreciation) Inputs")
        self.model_input_frames["Straight-Line Depreciation"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.model_input_frames["Double-Declining Balance Depreciation"] = self.model_input_frames["Straight-Line Depreciation"] # Same frame

        # Adjust common buttons and result frame positions relative to this GUI's grid
        self.result_frame.grid(row=start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=start_row + 2, column=0, columnspan=2, pady=5)


    def _hide_all_input_frames(self):
        """Hides all model-specific input frames by forgetting their grid positions."""
        # This is a bit tricky since some models share frames. We need to forget only unique frames.
        unique_frames = set(self.model_input_frames.values())
        for frame in unique_frames:
            frame.grid_forget()
        self.display_result("Select a model to view its inputs and calculate.", is_error=False)

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected model for Business/Accounting: {selected_model}")
        self._hide_all_input_frames()

        if selected_model in self.model_input_frames:
            # Show the frame associated with the selected model
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

            # Enable/disable specific inputs within the *active* frame based on the precise model
            self._update_specific_input_states_for_model(selected_model)
        else:
            self.display_result("Please select a valid model.", is_error=True)

    def _update_specific_input_states_for_model(self, selected_model: str):
        """
        Enables/disables individual input fields based on the currently selected model
        within a shared frame. This replaces the old _update_input_fields_state.
        """
        # First, ensure all inputs in the *currently displayed frame* are enabled.
        # This prevents leftover disabled states from previous selections.
        current_frame_field_keys = []
        if selected_model in ["Net Present Value (NPV)", "Internal Rate of Return (IRR)",
                              "Payback Period", "Discounted Payback Period", "Profitability Index (PI)"]:
            current_frame_field_keys = self.model_field_keys.get("Capital Budgeting Group", [])
        elif selected_model in ["Expected Loss (EL)", "Asset-Liability Gap"]:
            current_frame_field_keys = self.model_field_keys.get("Banking Risk Group", [])
        elif selected_model in ["Straight-Line Depreciation", "Double-Declining Balance Depreciation"]:
            current_frame_field_keys = self.model_field_keys.get("Depreciation Group", [])

        for key in current_frame_field_keys:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")

        # Now, apply specific disabling logic for the selected model
        if selected_model == "Payback Period":
            self.input_fields[self._get_field_key_from_label("Discount Rate (Annual %):")].config(state="disabled")
        
        elif selected_model == "Expected Loss (EL)":
            self.input_fields[self._get_field_key_from_label("Rate Sensitive Assets:")].config(state="disabled")
            self.input_fields[self._get_field_key_from_label("Rate Sensitive Liabilities:")].config(state="disabled")

        elif selected_model == "Asset-Liability Gap":
            self.input_fields[self._get_field_key_from_label("Probability of Default (PD, %):")].config(state="disabled")
            self.input_fields[self._get_field_key_from_label("Exposure at Default (EAD):")].config(state="disabled")
            self.input_fields[self._get_field_key_from_label("Loss Given Default (LGD, %):")].config(state="disabled")

        elif selected_model == "Straight-Line Depreciation":
            self.input_fields[self._get_field_key_from_label("Current Year (for DDB):")].config(state="disabled")

        self.display_result("Ready for calculation.", is_error=False)


    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Replicates the field key generation logic from BaseGUI's create_input_row.
        """
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    # --- Widget creation methods for each model group ---

    def _create_capital_budgeting_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Capital Budgeting Models (NPV, IRR, Payback, DPI, PI)."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Initial Investment:", "10000.00", "The initial cost of the project (enter as a positive number; it will be treated as an outflow for NPV/IRR).")
        field_keys.append(self._get_field_key_from_label("Initial Investment:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Cash Flows (comma-separated):", "3000,4000,5000,3000", "Project cash flows per period (e.g., 3000,4000,5000).")
        field_keys.append(self._get_field_key_from_label("Cash Flows (comma-separated):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Discount Rate (Annual %):", "10.00", "The annual discount rate for NPV, IRR, PI, and Discounted Payback.")
        field_keys.append(self._get_field_key_from_label("Discount Rate (Annual %):"))
        row_idx += 1
        
        # Store these keys under a group name, as these fields are shared by multiple models
        self.model_field_keys["Capital Budgeting Group"] = field_keys
        # Also, map individual models to this group's keys
        self.model_field_keys["Net Present Value (NPV)"] = field_keys
        self.model_field_keys["Internal Rate of Return (IRR)"] = field_keys
        self.model_field_keys["Payback Period"] = field_keys
        self.model_field_keys["Discounted Payback Period"] = field_keys
        self.model_field_keys["Profitability Index (PI)"] = field_keys

        return frame

    def _create_banking_risk_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Banking Risk Models (Expected Loss, A-L Gap)."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Probability of Default (PD, %):", "2.00", "Probability of a borrower defaulting, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Probability of Default (PD, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Exposure at Default (EAD):", "100000.00", "The outstanding amount when a borrower defaults.")
        field_keys.append(self._get_field_key_from_label("Exposure at Default (EAD):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Loss Given Default (LGD, %):", "40.00", "Percentage of EAD lost if default occurs.")
        field_keys.append(self._get_field_key_from_label("Loss Given Default (LGD, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Rate Sensitive Assets:", "5000000.00", "Assets whose interest rates will change with market rates.")
        field_keys.append(self._get_field_key_from_label("Rate Sensitive Assets:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Rate Sensitive Liabilities:", "4000000.00", "Liabilities whose interest rates will change with market rates.")
        field_keys.append(self._get_field_key_from_label("Rate Sensitive Liabilities:"))
        row_idx += 1

        self.model_field_keys["Banking Risk Group"] = field_keys
        self.model_field_keys["Expected Loss (EL)"] = field_keys # Map to group keys
        self.model_field_keys["Asset-Liability Gap"] = field_keys # Map to group keys

        return frame

    def _create_depreciation_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Depreciation Models (Straight-Line, DDB)."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Asset Cost:", "100000.00", "Initial cost of the asset.")
        field_keys.append(self._get_field_key_from_label("Asset Cost:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Salvage Value:", "10000.00", "Estimated residual value of the asset at the end of its useful life.")
        field_keys.append(self._get_field_key_from_label("Salvage Value:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Useful Life (Years):", "5", "Estimated number of years the asset will be used.") # Changed default to int for 'positive_integer' validation
        field_keys.append(self._get_field_key_from_label("Useful Life (Years):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Current Year (for DDB):", "1", "The specific year for which to calculate Double-Declining Balance depreciation.") # Changed default to int
        field_keys.append(self._get_field_key_from_label("Current Year (for DDB):"))
        row_idx += 1

        self.model_field_keys["Depreciation Group"] = field_keys
        self.model_field_keys["Straight-Line Depreciation"] = field_keys # Map to group keys
        self.model_field_keys["Double-Declining Balance Depreciation"] = field_keys # Map to group keys

        return frame

    # --- Calculation Logic ---

    def _parse_cash_flows(self, cash_flow_str: str, initial_investment: float = 0.0, is_for_npv_irr: bool = False) -> Union[List[float], str]:
        """
        Parses a comma-separated string of cash flows into a list of floats.
        Handles formatting for NPV/IRR (prepends -initial_investment) vs. other methods.
        Uses the centralized validate_input_list from BaseGUI.
        """
        is_valid, validated_flows = self.validate_input_list(cash_flow_str, 'numeric', "Cash Flows")

        if not is_valid:
            # If validation failed, validated_flows will contain the error message.
            return validated_flows

        cash_flows = list(validated_flows) # Ensure it's a mutable list

        if is_for_npv_irr:
            # For NPV/IRR, the first cash flow is typically the initial investment (as negative).
            # We must ensure it's always negative, regardless of user input sign.
            if initial_investment != 0: # Only prepend if there's an actual investment
                cash_flows.insert(0, -abs(initial_investment))
            elif initial_investment == 0 and not cash_flows: # If 0 investment and no cash flows
                 return "Cash Flows cannot be empty for NPV/IRR if initial investment is zero."

        return cash_flows


    def calculate_selected_model(self):
        """
        Retrieves inputs based on the selected model, validates them using BaseGUI's methods,
        performs the calculation, and displays the result.
        """
        self.display_result("Calculating...", is_error=False)
        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Model":
            self.display_result("Please select a model to calculate.", is_error=True)
            return

        # Determine which group of fields to read from based on the selected model
        group_key = ""
        if selected_model in self.model_field_keys and isinstance(self.model_field_keys[selected_model], list):
            # If the selected_model points directly to a list of keys, use it
            field_keys_for_model = self.model_field_keys[selected_model]
        else: # It's a model belonging to a group
            if selected_model in ["Net Present Value (NPV)", "Internal Rate of Return (IRR)",
                                  "Payback Period", "Discounted Payback Period", "Profitability Index (PI)"]:
                group_key = "Capital Budgeting Group"
            elif selected_model in ["Expected Loss (EL)", "Asset-Liability Gap"]:
                group_key = "Banking Risk Group"
            elif selected_model in ["Straight-Line Depreciation", "Double-Declining Balance Depreciation"]:
                group_key = "Depreciation Group"
            
            field_keys_for_model = self.model_field_keys.get(group_key, [])

        if not field_keys_for_model:
            self.display_result("Internal error: Field keys not found for selected model group.", is_error=True)
            logger.error(f"Field keys missing for model: {selected_model} (group: {group_key})")
            return

        # Prepare a dictionary to hold all validated inputs for the current calculation
        validated_inputs = {}
        all_valid = True

        # Extract values for relevant fields only
        for key in field_keys_for_model:
            value_str = self.get_input_value(key)
            field_name_for_display = key.replace('_', ' ').title()

            # Determine validation type based on specific field and model
            validation_type = 'numeric' # Default
            is_percentage_field = False
            
            if key == self._get_field_key_from_label("Initial Investment:"):
                validation_type = 'numeric' # Can be positive or negative for input, logic handles it
            elif key == self._get_field_key_from_label("Discount Rate (Annual %):"):
                is_percentage_field = True
            elif key == self._get_field_key_from_label("Probability of Default (PD, %):") or \
                 key == self._get_field_key_from_label("Loss Given Default (LGD, %):"):
                validation_type = 'numeric_range_0_100'
                is_percentage_field = True
            elif key == self._get_field_key_from_label("Exposure at Default (EAD):") or \
                 key == self._get_field_key_from_label("Rate Sensitive Assets:") or \
                 key == self._get_field_key_from_label("Rate Sensitive Liabilities:") or \
                 key == self._get_field_key_from_label("Asset Cost:"):
                validation_type = 'numeric' # Can be 0 or positive
            elif key == self._get_field_key_from_label("Salvage Value:"):
                validation_type = 'non_negative_numeric'
            elif key == self._get_field_key_from_label("Useful Life (Years):") or \
                 key == self._get_field_key_from_label("Current Year (for DDB):"):
                validation_type = 'positive_integer'
            
            # Special handling for cash flows - it's handled by _parse_cash_flows separately
            if key == self._get_field_key_from_label("Cash Flows (comma-separated):"):
                continue # Skip general validation here, handled below
            
            is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)
            
            if not is_valid:
                self.display_result(processed_value, is_error=True)
                all_valid = False
                return # Exit early on first validation error

            if is_percentage_field:
                processed_value /= 100.0

            validated_inputs[key] = processed_value

        try:
            result = None
            if selected_model in ["Net Present Value (NPV)", "Internal Rate of Return (IRR)",
                                  "Payback Period", "Discounted Payback Period", "Profitability Index (PI)"]:
                
                initial_investment = validated_inputs[self._get_field_key_from_label("Initial Investment:")]
                cash_flows_str = self.get_input_value(self._get_field_key_from_label("Cash Flows (comma-separated):"))
                
                # Different handling of initial investment for NPV/IRR vs others
                is_for_npv_irr = selected_model in ["Net Present Value (NPV)", "Internal Rate of Return (IRR)"]
                cash_flows_list = self._parse_cash_flows(cash_flows_str, initial_investment, is_for_npv_irr)

                if isinstance(cash_flows_list, str): # Error from _parse_cash_flows
                    return self.display_result(cash_flows_list, is_error=True)
                
                if not cash_flows_list:
                    self.display_result("Cash Flows cannot be empty.", is_error=True)
                    return

                if selected_model in ["Net Present Value (NPV)", "Discounted Payback Period", "Profitability Index (PI)"]:
                    discount_rate = validated_inputs[self._get_field_key_from_label("Discount Rate (Annual %):")]
                
                if selected_model == "Net Present Value (NPV)":
                    result = calculate_npv(discount_rate, cash_flows_list)
                    self.display_result(f"Net Present Value (NPV): {self.format_currency_output(result)}")
                elif selected_model == "Internal Rate of Return (IRR)":
                    if len(cash_flows_list) < 2:
                        self.display_result("At least two cash flows (including initial investment) are required for IRR.", is_error=True)
                        return
                    result_decimal = calculate_irr(cash_flows_list)
                    if result_decimal is None:
                        self.display_result("IRR could not be calculated. Check cash flow pattern.", is_error=True)
                    else:
                        self.display_result(f"Internal Rate of Return (IRR): {self.format_percentage_output(result_decimal)}")
                elif selected_model == "Payback Period":
                    result = calculate_payback_period(initial_investment, cash_flows_list)
                    if math.isinf(result):
                        self.display_result("Payback Period: Initial investment never fully recovered.", is_error=True)
                    else:
                        self.display_result(f"Payback Period: {self.format_number_output(result, 2)} years")
                elif selected_model == "Discounted Payback Period":
                    result = calculate_discounted_payback_period(initial_investment, cash_flows_list, discount_rate)
                    if math.isinf(result):
                        self.display_result("Discounted Payback Period: Initial investment never fully recovered.", is_error=True)
                    else:
                        self.display_result(f"Discounted Payback Period: {self.format_number_output(result, 2)} years")
                elif selected_model == "Profitability Index (PI)":
                    result = calculate_profitability_index(initial_investment, cash_flows_list, discount_rate)
                    self.display_result(f"Profitability Index (PI): {self.format_number_output(result, 4)}")

            elif selected_model == "Expected Loss (EL)":
                pd = validated_inputs[self._get_field_key_from_label("Probability of Default (PD, %):")]
                ead = validated_inputs[self._get_field_key_from_label("Exposure at Default (EAD):")]
                lgd = validated_inputs[self._get_field_key_from_label("Loss Given Default (LGD, %):")]
                
                result = calculate_expected_loss(pd, ead, lgd)
                self.display_result(f"Expected Loss (EL): {self.format_currency_output(result)}")
            elif selected_model == "Asset-Liability Gap":
                rsa = validated_inputs[self._get_field_key_from_label("Rate Sensitive Assets:")]
                rsl = validated_inputs[self._get_field_key_from_label("Rate Sensitive Liabilities:")]
                
                result = calculate_asset_liability_gap(rsa, rsl)
                self.display_result(f"Asset-Liability Gap: {self.format_currency_output(result)}")

            elif selected_model == "Straight-Line Depreciation":
                cost = validated_inputs[self._get_field_key_from_label("Asset Cost:")]
                salvage_value = validated_inputs[self._get_field_key_from_label("Salvage Value:")]
                useful_life = validated_inputs[self._get_field_key_from_label("Useful Life (Years):")]
                
                result = calculate_depreciation_straight_line(cost, salvage_value, useful_life)
                self.display_result(f"Annual Straight-Line Depreciation: {self.format_currency_output(result)}")
            elif selected_model == "Double-Declining Balance Depreciation":
                cost = validated_inputs[self._get_field_key_from_label("Asset Cost:")]
                salvage_value = validated_inputs[self._get_field_key_from_label("Salvage Value:")]
                useful_life = validated_inputs[self._get_field_key_from_label("Useful Life (Years):")]
                current_year = validated_inputs[self._get_field_key_from_label("Current Year (for DDB):")]

                if current_year > useful_life:
                    self.display_result("Current Year cannot be greater than Useful Life for DDB.", is_error=True)
                    return

                result = calculate_depreciation_double_declining_balance(cost, salvage_value, useful_life, current_year)
                self.display_result(f"DDB Depreciation for Year {current_year}: {self.format_currency_output(result)}")

        except ValueError as e:
            logger.error(f"Business/Accounting Calculation Error (ValueError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Business/Accounting Calculation Error (ZeroDivisionError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs like useful life or rates.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Business/Accounting calculation for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection
        and update the UI state.
        """
        super().clear_inputs()
        self.selected_model_var.set("Select a Model") # Reset combobox
        self._on_model_selected() # Trigger UI update to hide frames and clear messages

# Example usage (for testing BusinessAccountingGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Business & Accounting Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x850")

    #style = ttk.Style()
    #style.theme_use('clam')

    # For isolation testing, a simple frame acts as the parent
    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    business_accounting_gui = BusinessAccountingGUI(test_parent_frame, controller=None)
    business_accounting_gui.pack(fill="both", expand=True)

    root.mainloop()