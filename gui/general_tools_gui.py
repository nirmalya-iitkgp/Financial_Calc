# financial_calculator/gui/general_tools_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Union, List, Dict, Any
import re # Ensure this import is present

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import mathematical functions strictly as per PROJECT_STRUCTURE.md for general_tools_gui.py
from mathematical_functions.statistics import (
    calculate_descriptive_stats,
    perform_simple_linear_regression
)
from mathematical_functions.financial_basics import (
    calculate_perpetuity,
    calculate_growing_perpetuity
)
from mathematical_functions.forex import (
    convert_currency,
    calculate_forward_rate
)
from mathematical_functions.unit_conversions import (
    convert_time_periods
)

# Import constants (for formatting, if needed in the future directly)
from config import DEFAULT_WINDOW_WIDTH # for example usage

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GeneralToolsGUI(BaseGUI):
    """
    GUI module for General Financial and Statistical Tools, adhering to PROJECT_STRUCTURE.md.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="General Financial Tools", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Center the title
        self.scrollable_frame.grid_columnconfigure(1, weight=1) # Span across 2 columns

        # Variables for model selection
        self.selected_model_var = tk.StringVar(value="Select a Tool")

        # Dictionary to hold frames for each model group's inputs
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}
        # Dictionary to store the specific input field keys for each model
        self.model_field_keys: Dict[str, List[str]] = {}

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        self._create_all_tool_input_widgets(start_row=2) # Start below model selection

        self._hide_all_input_frames() # Hide all initially

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate Tool", command=self.calculate_selected_model)
        logger.info("GeneralToolsGUI initialized with functions from PROJECT_STRUCTURE.md.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific general tool."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select General Tool")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Tool:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.tool_options = [
            "Descriptive Statistics",
            "Simple Linear Regression",
            "Perpetuity Value",
            "Growing Perpetuity Value",
            "Currency Conversion",
            "Forward Rate",
            "Time Unit Conversion",
        ]
        self.model_combobox = ttk.Combobox(
            model_select_frame,
            textvariable=self.selected_model_var,
            values=self.tool_options,
            state="readonly"
        )
        self.model_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)

    def _create_all_tool_input_widgets(self, start_row: int):
        """
        Creates all input fields and frames for each general tool,
        but keeps them hidden initially.
        """
        parent_for_tools = self.scrollable_frame
        current_row = start_row

        self.model_input_frames["Descriptive Statistics"] = self._create_descriptive_stats_widgets(parent_for_tools, "Descriptive Statistics Inputs")
        self.model_input_frames["Descriptive Statistics"].grid(row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.model_input_frames["Simple Linear Regression"] = self._create_linear_regression_widgets(parent_for_tools, "Simple Linear Regression Inputs")
        self.model_input_frames["Simple Linear Regression"].grid(row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Perpetuity and Growing Perpetuity can share a frame, as they have overlapping inputs
        self.model_input_frames["Perpetuity_Group"] = self._create_perpetuity_widgets(parent_for_tools, "Perpetuity & Growing Perpetuity Inputs")
        self.model_input_frames["Perpetuity_Group"].grid(row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Currency Conversion and Forward Rate can share a frame
        self.model_input_frames["Forex_Group"] = self._create_forex_widgets(parent_for_tools, "Foreign Exchange Tools Inputs")
        self.model_input_frames["Forex_Group"].grid(row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.model_input_frames["Time Unit Conversion"] = self._create_unit_conversion_widgets(parent_for_tools, "Time Unit Conversion Inputs")
        self.model_input_frames["Time Unit Conversion"].grid(row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Adjust common buttons and result frame positions relative to this GUI's grid
        self.result_frame.grid(row=current_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=current_row + 2, column=0, columnspan=2, pady=5)

    def _hide_all_input_frames(self):
        """Hides all model-specific input frames by forgetting their grid positions."""
        for frame in self.model_input_frames.values():
            frame.grid_forget()
        self.display_result("Select a tool to view its inputs and calculate.", is_error=False)

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected tool for General Tools: {selected_model}")
        self._hide_all_input_frames()

        frame_to_show = None
        # Handle showing the correct frame and updating specific fields within shared frames
        if selected_model == "Descriptive Statistics":
            frame_to_show = self.model_input_frames["Descriptive Statistics"]
        elif selected_model == "Simple Linear Regression":
            frame_to_show = self.model_input_frames["Simple Linear Regression"]
        elif selected_model in ["Perpetuity Value", "Growing Perpetuity Value"]:
            frame_to_show = self.model_input_frames["Perpetuity_Group"]
            self._update_specific_perpetuity_states(selected_model)
        elif selected_model in ["Currency Conversion", "Forward Rate"]:
            frame_to_show = self.model_input_frames["Forex_Group"]
            self._update_specific_forex_states(selected_model)
        elif selected_model == "Time Unit Conversion":
            frame_to_show = self.model_input_frames["Time Unit Conversion"]
        else:
            self.display_result("Please select a valid tool.", is_error=True)
            return

        if frame_to_show:
            # Re-grid the selected frame
            frame_to_show.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
            self.display_result("Ready for calculation.", is_error=False)
        else:
            self.display_result("Error: Could not find frame for selected tool.", is_error=True)

    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Replicates the field key generation logic from BaseGUI's create_input_row.
        """
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    def _update_specific_perpetuity_states(self, selected_model: str):
        """
        Manages enabling/disabling fields within the shared Perpetuity_Group frame.
        """
        all_perpetuity_fields = self.model_field_keys["Perpetuity_Group"]

        # First, enable all fields in this group
        for key in all_perpetuity_fields:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")

        # Then, disable specific ones based on the sub-selection
        if selected_model == "Perpetuity Value":
            self.input_fields[self._get_field_key_from_label("Growth Rate (%):")].config(state="disabled")
        elif selected_model == "Growing Perpetuity Value":
            # All fields are needed
            pass

    def _update_specific_forex_states(self, selected_model: str):
        """
        Manages enabling/disabling fields within the shared Forex_Group frame.
        """
        all_forex_fields = self.model_field_keys["Forex_Group"]

        # First, enable all fields in this group
        for key in all_forex_fields:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")

        # Then, disable specific ones based on the sub-selection
        if selected_model == "Currency Conversion":
            self.input_fields[self._get_field_key_from_label("Domestic Rate (%):")].config(state="disabled")
            self.input_fields[self._get_field_key_from_label("Foreign Rate (%):")].config(state="disabled")
            self.input_fields[self._get_field_key_from_label("Time to Maturity (Years):")].config(state="disabled")
        elif selected_model == "Forward Rate":
            self.input_fields[self._get_field_key_from_label("Amount to Convert:")].config(state="disabled")
            # Other fields are needed for Forward Rate

    # --- Widget creation methods for each tool group ---

    def _create_descriptive_stats_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Descriptive Statistics."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        key = self._get_field_key_from_label("Data (comma-separated):")
        self.create_input_row(frame, 0, "Data (comma-separated):", "1,2,3,4,5", "Enter numbers separated by commas (e.g., 1, 2.5, 3).")
        self.model_field_keys["Descriptive Statistics"] = [key]
        return frame

    def _create_linear_regression_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Simple Linear Regression."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        keys = []
        key_x = self._get_field_key_from_label("X Data (comma-separated):")
        key_y = self._get_field_key_from_label("Y Data (comma-separated):")

        self.create_input_row(frame, 0, "X Data (comma-separated):", "1,2,3,4,5", "Enter X values separated by commas.")
        self.create_input_row(frame, 1, "Y Data (comma-separated):", "2,4,5,4,5", "Enter Y values separated by commas.")
        
        keys.append(key_x)
        keys.append(key_y)
        self.model_field_keys["Simple Linear Regression"] = keys
        return frame

    def _create_perpetuity_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Perpetuity and Growing Perpetuity."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        keys = []
        key_pmt = self._get_field_key_from_label("Payment (PMT):")
        key_dr = self._get_field_key_from_label("Discount Rate (%):")
        key_gr = self._get_field_key_from_label("Growth Rate (%):")

        self.create_input_row(frame, 0, "Payment (PMT):", "100.00", "Regular payment amount.")
        self.create_input_row(frame, 1, "Discount Rate (%):", "5.00", "Discount rate as a percentage (e.g., 5 for 5%).")
        self.create_input_row(frame, 2, "Growth Rate (%):", "2.00", "Growth rate as a percentage (for growing perpetuity, 0 if not growing).")
        
        keys.extend([key_pmt, key_dr, key_gr])
        self.model_field_keys["Perpetuity_Group"] = keys # Use a group key for the shared frame
        self.model_field_keys["Perpetuity Value"] = [key_pmt, key_dr]
        self.model_field_keys["Growing Perpetuity Value"] = [key_pmt, key_dr, key_gr]

        return frame

    def _create_forex_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Forex Conversion and Forward Rate."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        keys = []
        key_amount = self._get_field_key_from_label("Amount to Convert:")
        key_spot = self._get_field_key_from_label("Spot Rate (From/To):")
        key_dr = self._get_field_key_from_label("Domestic Rate (%):")
        key_fr = self._get_field_key_from_label("Foreign Rate (%):")
        key_time = self._get_field_key_from_label("Time to Maturity (Years):")

        self.create_input_row(frame, 0, "Amount to Convert:", "100.00", "Amount in the 'From' currency.")
        self.create_input_row(frame, 1, "Spot Rate (From/To):", "1.10", "e.g., 1.10 for EUR/USD if converting EUR to USD (1 EUR = 1.10 USD).")
        self.create_input_row(frame, 2, "Domestic Rate (%):", "2.00", "Annual interest rate in the domestic currency (e.g., USD).")
        self.create_input_row(frame, 3, "Foreign Rate (%):", "1.50", "Annual interest rate in the foreign currency (e.g., EUR).")
        self.create_input_row(frame, 4, "Time to Maturity (Years):", "1.00", "Time period for forward rate calculation (in years).")
        
        # Manually added Entry fields for currency codes
        ttk.Label(frame, text="Current Currency:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.current_currency_var = tk.StringVar(value="USD") # Default
        self.current_currency_entry = ttk.Entry(frame, textvariable=self.current_currency_var, width=10)
        self.current_currency_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        # Store for state management and value retrieval, using a consistent key format
        self.input_fields["current_currency"] = self.current_currency_entry
        key_cc = "current_currency" # Manually define key for non-create_input_row fields

        ttk.Label(frame, text="Target Currency:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.target_currency_var = tk.StringVar(value="EUR") # Default
        self.target_currency_entry = ttk.Entry(frame, textvariable=self.target_currency_var, width=10)
        self.target_currency_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.input_fields["target_currency"] = self.target_currency_entry
        key_tc = "target_currency" # Manually define key

        keys.extend([key_amount, key_spot, key_dr, key_fr, key_time, key_cc, key_tc])
        self.model_field_keys["Forex_Group"] = keys # Use a group key for the shared frame
        self.model_field_keys["Currency Conversion"] = [key_amount, key_spot, key_cc, key_tc]
        self.model_field_keys["Forward Rate"] = [key_spot, key_dr, key_fr, key_time, key_cc, key_tc]

        return frame

    def _create_unit_conversion_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Unit Conversion."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        keys = []
        key_value = self._get_field_key_from_label("Value to Convert:")
        key_from_unit = self._get_field_key_from_label("From Unit:")
        key_to_unit = self._get_field_key_from_label("To Unit:")

        self.create_input_row(frame, 0, "Value to Convert:", "12", "The numeric value to convert.")
        self.create_input_row(frame, 1, "From Unit:", "months", "e.g., 'days', 'weeks', 'months', 'quarters', 'years'.")
        self.create_input_row(frame, 2, "To Unit:", "years", "e.g., 'days', 'weeks', 'months', 'quarters', 'years'.")
        
        keys.extend([key_value, key_from_unit, key_to_unit])
        self.model_field_keys["Time Unit Conversion"] = keys
        return frame


    # --- Calculation Logic ---

    def calculate_selected_model(self):
        """
        Performs the selected General Tool calculation based on user inputs.
        """
        self.display_result("Calculating...", is_error=False)
        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Tool":
            self.display_result("Please select a general tool to calculate.", is_error=True)
            return

        # Get the specific field keys for the selected model
        field_keys_for_model = self.model_field_keys.get(selected_model, [])
        # If the model is part of a group, get its specific keys from the group's definition
        if not field_keys_for_model:
            if selected_model in ["Perpetuity Value", "Growing Perpetuity Value"]:
                field_keys_for_model = self.model_field_keys.get(selected_model, []) # Correctly gets the specific ones
            elif selected_model in ["Currency Conversion", "Forward Rate"]:
                field_keys_for_model = self.model_field_keys.get(selected_model, []) # Correctly gets the specific ones
            
        if not field_keys_for_model:
            self.display_result("Internal error: Field keys not found for selected tool.", is_error=True)
            logger.error(f"Field keys missing for tool: {selected_model}")
            return

        # Prepare a dictionary to hold all validated inputs for the current calculation
        validated_inputs = {}

        try:
            # Extract and validate values for relevant fields
            for key in field_keys_for_model:
                value_str = self.get_input_value(key)
                # Fallback to the display label if key not directly from label generation
                field_name_for_display = key.replace('_', ' ').title() 
                if key == "current_currency": field_name_for_display = "Current Currency"
                if key == "target_currency": field_name_for_display = "Target Currency"

                validation_type = 'numeric' # Default
                # Determine validation type based on key/common patterns
                if 'data_comma_separated' in key:
                    validation_type = 'numeric_list'
                elif 'value_to_convert' in key:
                    validation_type = 'numeric'
                elif 'amount_to_convert' in key or 'spot_rate_from_to' in key or \
                     'payment_pmt' in key:
                    validation_type = 'positive_numeric_or_zero' # Allow 0 for payment/amount if meaningful
                elif 'rate' in key or 'time' in key:
                    validation_type = 'numeric' # Rates/time can be zero, but not necessarily positive
                elif 'unit' in key or 'currency' in key:
                    validation_type = 'string_not_empty' # For text fields

                is_valid, processed_value = None, None
                if validation_type == 'numeric_list':
                    is_valid, processed_value = self.validate_input_list(value_str, 'numeric', field_name_for_display)
                elif validation_type == 'string_not_empty':
                    if not value_str.strip():
                        is_valid, processed_value = False, f"{field_name_for_display} cannot be empty."
                    else:
                        is_valid, processed_value = True, value_str.strip()
                elif validation_type == 'positive_numeric_or_zero':
                     is_valid, processed_value = self.validate_input(value_str, 'numeric', field_name_for_display)
                     if is_valid and processed_value < 0:
                         is_valid, processed_value = False, f"{field_name_for_display} must be positive or zero."
                else: # Default numeric validation
                    is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)
                
                if not is_valid:
                    return self.display_result(processed_value, is_error=True)

                # Convert percentages to decimals *after* validation
                if 'rate' in key or 'yield' in key or 'growth_rate' in key and processed_value is not None:
                    # Apply conversion only if the field value is indeed a percentage
                    # This check makes sure we don't convert currency codes or other non-percentage numbers
                    if selected_model in ["Perpetuity Value", "Growing Perpetuity Value", "Forward Rate"]:
                        if key in [self._get_field_key_from_label("Discount Rate (%):"),
                                   self._get_field_key_from_label("Growth Rate (%):"),
                                   self._get_field_key_from_label("Domestic Rate (%):"),
                                   self._get_field_key_from_label("Foreign Rate (%):")]:
                            processed_value /= 100.0

                validated_inputs[key] = processed_value
            
            # --- Perform Calculation based on selected_model ---
            if selected_model == "Descriptive Statistics":
                data_list = validated_inputs.get(self._get_field_key_from_label("Data (comma-separated):"))
                if not data_list: return self.display_result("Data list cannot be empty.", is_error=True)
                stats_result = calculate_descriptive_stats(data_list)
                output_str = "Descriptive Statistics:\n"
                for stat, value in stats_result.items():
                    output_str += f"{stat.replace('_', ' ').title()}: {self.format_number_output(value, 4)}\n"
                self.display_result(output_str.strip())
            
            elif selected_model == "Simple Linear Regression":
                x_data = validated_inputs.get(self._get_field_key_from_label("X Data (comma-separated):"))
                y_data = validated_inputs.get(self._get_field_key_from_label("Y Data (comma-separated):"))

                if not x_data or not y_data: return self.display_result("X and Y data lists cannot be empty.", is_error=True)
                if len(x_data) != len(y_data):
                    self.display_result("X and Y data lists must have the same number of elements.", is_error=True)
                    return
                if len(x_data) < 2:
                    self.display_result("At least two data points are required for linear regression.", is_error=True)
                    return

                slope, intercept, r_squared = perform_simple_linear_regression(x_data, y_data)
                result_str = (
                    f"Simple Linear Regression:\n"
                    f"Slope (m): {self.format_number_output(slope, 6)}\n"
                    f"Intercept (b): {self.format_number_output(intercept, 6)}\n"
                    f"R-squared: {self.format_number_output(r_squared, 6)}"
                )
                self.display_result(result_str)

            elif selected_model == "Perpetuity Value":
                payment = validated_inputs.get(self._get_field_key_from_label("Payment (PMT):"))
                rate = validated_inputs.get(self._get_field_key_from_label("Discount Rate (%):"))
                
                if rate <= 0:
                    self.display_result("Discount Rate must be positive for Perpetuity Value.", is_error=True)
                    return

                result = calculate_perpetuity(payment, rate)
                self.display_result(f"Perpetuity Value: {self.format_currency_output(result)}")

            elif selected_model == "Growing Perpetuity Value":
                payment = validated_inputs.get(self._get_field_key_from_label("Payment (PMT):"))
                rate = validated_inputs.get(self._get_field_key_from_label("Discount Rate (%):"))
                growth_rate = validated_inputs.get(self._get_field_key_from_label("Growth Rate (%):"))

                if rate <= growth_rate:
                    self.display_result("Discount Rate must be greater than Growth Rate for Growing Perpetuity.", is_error=True)
                    return

                result = calculate_growing_perpetuity(payment, rate, growth_rate)
                self.display_result(f"Growing Perpetuity Value: {self.format_currency_output(result)}")

            elif selected_model == "Currency Conversion":
                amount = validated_inputs.get(self._get_field_key_from_label("Amount to Convert:"))
                spot_rate = validated_inputs.get(self._get_field_key_from_label("Spot Rate (From/To):"))
                from_currency = validated_inputs.get("current_currency")
                to_currency = validated_inputs.get("target_currency")

                converted_amount = convert_currency(amount, spot_rate)
                self.display_result(f"{self.format_currency_output(amount, currency_symbol=from_currency)} is equal to {self.format_currency_output(converted_amount, currency_symbol=to_currency)}")

            elif selected_model == "Forward Rate":
                spot_rate = validated_inputs.get(self._get_field_key_from_label("Spot Rate (From/To):"))
                domestic_rate = validated_inputs.get(self._get_field_key_from_label("Domestic Rate (%):"))
                foreign_rate = validated_inputs.get(self._get_field_key_from_label("Foreign Rate (%):"))
                time = validated_inputs.get(self._get_field_key_from_label("Time to Maturity (Years):"))
                
                from_currency = validated_inputs.get("current_currency")
                to_currency = validated_inputs.get("target_currency")

                forward_rate = calculate_forward_rate(spot_rate, domestic_rate, foreign_rate, time)
                self.display_result(f"Calculated Forward Rate ({from_currency}/{to_currency}): {self.format_number_output(forward_rate, 6)}")

            elif selected_model == "Time Unit Conversion":
                value = validated_inputs.get(self._get_field_key_from_label("Value to Convert:"))
                from_unit = validated_inputs.get(self._get_field_key_from_label("From Unit:"))
                to_unit = validated_inputs.get(self._get_field_key_from_label("To Unit:"))

                try:
                    converted_value = convert_time_periods(value, from_unit, to_unit)
                    self.display_result(f"{self.format_number_output(value, 4)} {from_unit} is {self.format_number_output(converted_value, 4)} {to_unit}")
                except ValueError as unit_error:
                    self.display_result(f"Unit Conversion Error: {unit_error}", is_error=True)
                    return

            else:
                self.display_result("Please select a calculation type.", is_error=True)

        except ValueError as e:
            logger.error(f"General Tools Calculation Error (ValueError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"General Tools Calculation Error (ZeroDivisionError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during General Tools calculation for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection,
        and currency fields, then updates the UI state.
        """
        super().clear_inputs()
        self.selected_model_var.set("Select a Tool") # Reset combobox
        # Reset the manually added currency fields
        self.current_currency_var.set("USD")
        self.target_currency_var.set("EUR")
        self._on_model_selected() # Trigger UI update to hide frames and clear messages

# Example usage (for testing GeneralToolsGUI in isolation if desired)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("General Financial Tools Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x850")

    # style = ttk.Style()
    # style.theme_use('clam')

    # For isolation testing, a simple frame acts as the parent
    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    general_tools_gui = GeneralToolsGUI(test_parent_frame, controller=None)
    general_tools_gui.pack(fill="both", expand=True)

    root.mainloop()