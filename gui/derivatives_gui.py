# financial_calculator/gui/derivatives_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Union, List, Dict, Any
import re # Needed for field key generation consistency

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import Derivatives mathematical functions as per PROJECT_STRUCTURE.md
# From options_bsm.py (keeping for reference, but will primarily use generic black_scholes_option_price)
from mathematical_functions.options_bsm import (
    black_scholes_call_price, # Specific call
    black_scholes_put_price   # Specific put
)
# From option_greeks.py
from mathematical_functions.option_greeks import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_vega,
    black_scholes_theta,
    black_scholes_rho
)
# From derivatives_advanced.py (preferred for generic BSM and other derivatives)
from mathematical_functions.derivatives_advanced import (
    binomial_option_price,
    black_scholes_option_price, # Generic BSM call/put
    calculate_futures_price
)

# Import constants (for formatting, if needed in the future directly)
from config import DEFAULT_WINDOW_WIDTH # for example usage

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DerivativesGUI(BaseGUI):
    """
    GUI module for Derivatives (Options & Futures) calculations.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        
        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Derivatives Models", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Center the title
        self.scrollable_frame.grid_columnconfigure(1, weight=1) # Span across 2 columns

        # Variables for model selection
        self.selected_model_var = tk.StringVar(value="Select a Model")
        self.option_type_var = tk.StringVar(value="CALL")   # Default: Call (remains radio button)
        self.option_style_var = tk.StringVar(value="EUROPEAN") # Default: European (remains radio button)

        # Dictionary to hold frames for each model group's inputs
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}
        # Dictionary to store the specific input field keys for each model
        self.model_field_keys: Dict[str, List[str]] = {}

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        self._create_all_model_input_widgets(start_row=2) # Start below model selection

        self._hide_all_input_frames() # Hide all initially

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate Derivative", command=self.calculate_selected_model)
        logger.info("DerivativesGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific derivative model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Derivative Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Black-Scholes Option Price",
            "Binomial Option Price",
            "All Option Greeks",
            "Futures Price"
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
        Creates all input fields and frames for each derivative model,
        but keeps them hidden initially.
        """
        parent_for_models = self.scrollable_frame

        # Options related inputs (BSM, Binomial, Greeks) - share one frame
        self.model_input_frames["Options_Group"] = self._create_option_widgets(parent_for_models, "Option Pricing Inputs")
        self.model_input_frames["Options_Group"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Futures related inputs - separate frame
        self.model_input_frames["Futures_Group"] = self._create_futures_widgets(parent_for_models, "Futures Pricing Inputs")
        self.model_input_frames["Futures_Group"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Adjust common buttons and result frame positions relative to this GUI's grid
        self.result_frame.grid(row=start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=start_row + 2, column=0, columnspan=2, pady=5)

    def _hide_all_input_frames(self):
        """Hides all model-specific input frames by forgetting their grid positions."""
        for frame in self.model_input_frames.values():
            frame.grid_forget()
        self.display_result("Select a model to view its inputs and calculate.", is_error=False)

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected model for Derivatives: {selected_model}")
        self._hide_all_input_frames()

        # Determine which group frame to show
        if selected_model in ["Black-Scholes Option Price", "Binomial Option Price", "All Option Greeks"]:
            frame_to_show = self.model_input_frames["Options_Group"]
            self._update_specific_option_input_states(selected_model)
        elif selected_model == "Futures Price":
            frame_to_show = self.model_input_frames["Futures_Group"]
            self._update_specific_futures_input_states(selected_model)
        else:
            self.display_result("Please select a valid model.", is_error=True)
            return

        frame_to_show.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.display_result("Ready for calculation.", is_error=False)

    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Replicates the field key generation logic from BaseGUI's create_input_row.
        """
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    def _update_specific_option_input_states(self, selected_model: str):
        """
        Enables/disables individual input fields and option type/style radio buttons
        within the 'Options_Group' frame based on the selected option model.
        """
        # All relevant option-specific fields in this group
        option_fields_to_manage = self.model_field_keys["Options_Group"]

        # First, enable all fields that are part of the 'Options_Group'
        for key in option_fields_to_manage:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")
        
        # Enable option type/style radio buttons
        for rb in self.option_type_radiobuttons + self.option_style_radiobuttons:
            rb.config(state="normal")

        # Now, apply specific disabling logic based on the precise model
        if selected_model == "Black-Scholes Option Price" or selected_model == "All Option Greeks":
            # BSM and Greeks do not use Number of Steps
            self.input_fields[self._get_field_key_from_label("Number of Steps (Binomial):")].config(state="disabled")
            if self.option_style_var.get() == "AMERICAN":
                # Only European style is generally supported for BSM and direct Greeks
                self.display_result("Black-Scholes-Merton model and its Greeks are for European options only.", is_error=True)
            else:
                 self.display_result("Ready for calculation.", is_error=False) # Clear previous warning

        elif selected_model == "Binomial Option Price":
            # Binomial uses all option inputs including number of steps
            self.display_result("Ready for Binomial Option Pricing.", is_error=False)

    def _update_specific_futures_input_states(self, selected_model: str):
        """
        Enables/disables individual input fields within the 'Futures_Group' frame.
        """
        # All relevant futures-specific fields in this group
        futures_fields_to_manage = self.model_field_keys["Futures Price"]

        # First, enable all fields that are part of the 'Futures_Group'
        for key in futures_fields_to_manage:
            if key in self.input_fields:
                self.input_fields[key].config(state="normal")

        # Disable option type/style radio buttons (they are not in this frame, but manage state for completeness)
        for rb in self.option_type_radiobuttons + self.option_style_radiobuttons:
            rb.config(state="disabled")

        self.display_result("Ready for Futures Price calculation.", is_error=False)


    # --- Widget creation methods for each model group ---

    def _create_option_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Option Pricing and Greeks."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Spot Price (S):", "100.00", "Current market price of the underlying asset.")
        field_keys.append(self._get_field_key_from_label("Spot Price (S):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Strike Price (K):", "100.00", "The price at which the option can be exercised.")
        field_keys.append(self._get_field_key_from_label("Strike Price (K):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Time to Maturity (T, years):", "0.50", "Time until option expiration, in years (e.g., 0.5 for 6 months).")
        field_keys.append(self._get_field_key_from_label("Time to Maturity (T, years):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Risk-Free Rate (Annual %):", "5.00", "Annual risk-free interest rate as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (Annual %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Volatility (Annual %):", "20.00", "Annualized volatility of the underlying asset as a percentage.")
        field_keys.append(self._get_field_key_from_label("Volatility (Annual %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Dividend Yield (q, Annual %):", "0.00", "Annual dividend yield as a percentage.")
        field_keys.append(self._get_field_key_from_label("Dividend Yield (q, Annual %):"))
        row_idx += 1
        
        self.create_input_row(frame, row_idx, "Number of Steps (Binomial):", "100", "Number of steps in the binomial tree model.")
        field_keys.append(self._get_field_key_from_label("Number of Steps (Binomial):"))
        row_idx += 1

        # Option Type & Style Selection (These remain radio buttons as they are parameters)
        option_spec_subframe = ttk.LabelFrame(frame, text="Option Type & Style")
        option_spec_subframe.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        option_spec_subframe.grid_columnconfigure(0, weight=1) # Allow expansion
        option_spec_subframe.grid_columnconfigure(1, weight=1)
        option_spec_subframe.grid_columnconfigure(2, weight=1)

        ttk.Label(option_spec_subframe, text="Type:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.option_type_radiobuttons = [
            ttk.Radiobutton(option_spec_subframe, text="Call", variable=self.option_type_var, value="CALL", command=self._on_model_selected),
            ttk.Radiobutton(option_spec_subframe, text="Put", variable=self.option_type_var, value="PUT", command=self._on_model_selected)
        ]
        self.option_type_radiobuttons[0].grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.option_type_radiobuttons[1].grid(row=0, column=2, padx=5, pady=2, sticky="w")

        ttk.Label(option_spec_subframe, text="Style:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.option_style_radiobuttons = [
            ttk.Radiobutton(option_spec_subframe, text="European", variable=self.option_style_var, value="EUROPEAN", command=self._on_model_selected),
            ttk.Radiobutton(option_spec_subframe, text="American", variable=self.option_style_var, value="AMERICAN", command=self._on_model_selected)
        ]
        self.option_style_radiobuttons[0].grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.option_style_radiobuttons[1].grid(row=1, column=2, padx=5, pady=2, sticky="w")

        # Store these keys under a group name, as these fields are shared by multiple option models
        self.model_field_keys["Options_Group"] = field_keys
        # Also, map individual models to this group's keys
        self.model_field_keys["Black-Scholes Option Price"] = field_keys
        self.model_field_keys["Binomial Option Price"] = field_keys
        self.model_field_keys["All Option Greeks"] = field_keys

        return frame

    def _create_futures_widgets(self, parent_frame: ttk.Frame, title: str) -> ttk.LabelFrame:
        """Creates widgets for Futures Pricing."""
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Spot Price (S):", "100.00", "Current market price of the underlying asset for futures.")
        field_keys.append(self._get_field_key_from_label("Spot Price (S):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Time to Maturity (T, years):", "0.50", "Time until futures expiration, in years.")
        field_keys.append(self._get_field_key_from_label("Time to Maturity (T, years):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Risk-Free Rate (Annual %):", "5.00", "Annual risk-free interest rate as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (Annual %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Cost of Carry (Annual %):", "0.00", "Cost of holding the underlying asset (e.g., storage, insurance, negative if dividends).")
        field_keys.append(self._get_field_key_from_label("Cost of Carry (Annual %):"))
        row_idx += 1

        self.model_field_keys["Futures Price"] = field_keys # Map directly to its own keys

        return frame

    # --- Calculation Logic ---

    def calculate_selected_model(self):
        """
        Performs the Derivatives calculation based on user inputs and selected model.
        """
        self.display_result("Calculating...", is_error=False)
        selected_model = self.selected_model_var.get()
        option_type = self.option_type_var.get() # "CALL" or "PUT"
        option_style = self.option_style_var.get() # "EUROPEAN" or "AMERICAN"

        if selected_model == "Select a Model":
            self.display_result("Please select a derivative model to calculate.", is_error=True)
            return

        # Determine which set of field keys to use for validation
        field_keys_for_model: List[str] = []
        if selected_model in ["Black-Scholes Option Price", "Binomial Option Price", "All Option Greeks"]:
            field_keys_for_model = self.model_field_keys.get("Options_Group", [])
        elif selected_model == "Futures Price":
            field_keys_for_model = self.model_field_keys.get("Futures Price", [])
        
        if not field_keys_for_model:
            self.display_result("Internal error: Field keys not found for selected model.", is_error=True)
            logger.error(f"Field keys missing for model: {selected_model}")
            return

        # Prepare a dictionary to hold all validated inputs for the current calculation
        validated_inputs = {}

        try:
            # Extract and validate values for relevant fields
            for key in field_keys_for_model:
                value_str = self.get_input_value(key)
                field_name_for_display = key.replace('_', ' ').title()

                validation_type = 'numeric' # Default

                if key == self._get_field_key_from_label("Spot Price (S):") or \
                   key == self._get_field_key_from_label("Strike Price (K):") or \
                   key == self._get_field_key_from_label("Volatility (Annual %):") or \
                   key == self._get_field_key_from_label("Time to Maturity (T, years):"):
                    validation_type = 'positive_numeric'
                elif key == self._get_field_key_from_label("Number of Steps (Binomial):"):
                    validation_type = 'positive_integer'
                elif key == self._get_field_key_from_label("Risk-Free Rate (Annual %):") or \
                     key == self._get_field_key_from_label("Dividend Yield (q, Annual %):") or \
                     key == self._get_field_key_from_label("Cost of Carry (Annual %):"):
                    validation_type = 'numeric' # Can be negative

                is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)
                
                if not is_valid:
                    return self.display_result(processed_value, is_error=True)

                # Convert percentages to decimals
                if "%" in field_name_for_display: # Generic check for percentage fields
                    processed_value /= 100.0

                validated_inputs[key] = processed_value
            
            # Retrieve validated values (using .get() with default 0.0 for potentially disabled fields)
            s = validated_inputs.get(self._get_field_key_from_label("Spot Price (S):"), 0.0)
            k = validated_inputs.get(self._get_field_key_from_label("Strike Price (K):"), 0.0)
            t = validated_inputs.get(self._get_field_key_from_label("Time to Maturity (T, years):"), 0.0)
            r = validated_inputs.get(self._get_field_key_from_label("Risk-Free Rate (Annual %):"), 0.0)
            sigma = validated_inputs.get(self._get_field_key_from_label("Volatility (Annual %):"), 0.0)
            q = validated_inputs.get(self._get_field_key_from_label("Dividend Yield (q, Annual %):"), 0.0)
            n_steps = int(validated_inputs.get(self._get_field_key_from_label("Number of Steps (Binomial):"), 0))
            cost_of_carry = validated_inputs.get(self._get_field_key_from_label("Cost of Carry (Annual %):"), 0.0)

            # Specific validation for volatility
            if selected_model in ["Black-Scholes Option Price", "Binomial Option Price", "All Option Greeks"] and t > 0 and sigma == 0:
                self.display_result("Volatility cannot be zero for option pricing/Greeks if time to maturity is positive.", is_error=True)
                return

            # --- Perform Calculation ---
            if selected_model == "Black-Scholes Option Price":
                if option_style == "AMERICAN":
                    self.display_result("Black-Scholes-Merton model is designed for European options only. For American options, please select Binomial.", is_error=True)
                    return
                
                price = black_scholes_option_price(s, k, t, r, sigma, option_type, q)
                self.display_result(f"Black-Scholes {option_type} Price: {self.format_currency_output(price)}")

            elif selected_model == "Binomial Option Price":
                price = binomial_option_price(s, k, t, r, sigma, n_steps, option_type, option_style == "AMERICAN", q)
                self.display_result(f"Binomial {option_style} {option_type} Price ({n_steps} steps): {self.format_currency_output(price)}")

            elif selected_model == "All Option Greeks":
                if option_style == "AMERICAN":
                    self.display_result("Option Greeks (Black-Scholes based) are generally for European options only. Consider numerical methods for American option Greeks.", is_error=True)
                    return

                delta_val = black_scholes_delta(s, k, t, r, sigma, option_type, q)
                gamma_val = black_scholes_gamma(s, k, t, r, sigma, q)
                vega_val = black_scholes_vega(s, k, t, r, sigma, q)
                theta_val = black_scholes_theta(s, k, t, r, sigma, option_type, q)
                rho_val = black_scholes_rho(s, k, t, r, sigma, option_type, q)

                result_msg = (
                    f"Option Greeks for {option_type} (European):\n"
                    f"  Delta: {self.format_number_output(delta_val, 4)}\n"
                    f"  Gamma: {self.format_number_output(gamma_val, 4)}\n"
                    f"  Vega: {self.format_number_output(vega_val, 4)} (per 1% change in σ)\n"
                    f"  Theta: {self.format_number_output(theta_val, 4)} (per year)\n"
                    f"  Rho: {self.format_number_output(rho_val, 4)} (per 1% change in r)"
                )
                self.display_result(result_msg)

            elif selected_model == "Futures Price":
                price = calculate_futures_price(s, r, t, cost_of_carry)
                self.display_result(f"Futures Price: {self.format_currency_output(price)}")

        except ValueError as e:
            logger.error(f"Derivatives Calculation Error (ValueError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Derivatives Calculation Error (ZeroDivisionError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Derivatives calculation for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection,
        option type, and option style, and update the UI state.
        """
        super().clear_inputs()
        self.selected_model_var.set("Select a Model") # Reset combobox
        self.option_type_var.set("CALL")   # Reset option type
        self.option_style_var.set("EUROPEAN") # Reset option style
        self._on_model_selected() # Trigger UI update to hide frames and clear messages

# Example usage (for testing DerivativesGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Derivatives Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x750")

    # style = ttk.Style()
    # style.theme_use('clam')

    # For isolation testing, a simple frame acts as the parent
    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    derivatives_gui = DerivativesGUI(test_parent_frame, controller=None)
    derivatives_gui.pack(fill="both", expand=True)

    root.mainloop()