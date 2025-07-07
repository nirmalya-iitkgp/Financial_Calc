# financial_calculator/gui/commodity_real_estate_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, List, Callable, Union
import re # Needed for field key generation consistency if not purely relying on BaseGUI's internal self.input_fields

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import mathematical functions as per the agreed structure
from mathematical_functions.commodity_finance import (
    calculate_commodity_futures_price_cost_of_carry,
    calculate_schwartz_smith_futures_price
)
from mathematical_functions.private_markets_valuation import (
    calculate_real_estate_terminal_value_gordon_growth
)

# Import utility functions (these are handled by BaseGUI's methods now, but import for direct use if needed)
# from utils.validation import ...
# from utils.helper_functions import ...
from config import ( # Still needed for formatting constants if using directly
    DEFAULT_DECIMAL_PLACES_CURRENCY, DEFAULT_DECIMAL_PLACES_PERCENTAGE,
    DEFAULT_DECIMAL_PLACES_GENERAL, DEFAULT_WINDOW_WIDTH
)


# Set up logging for this module
logger = logging.getLogger(__name__)
# Ensure basicConfig is only called once by the root logger or by the main app.
# If not already configured by main_app.py, this fallback ensures logging works for standalone runs.
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class CommodityAndRealEstateFinanceGUI(BaseGUI):
    """
    GUI module for Commodity Futures and Real Estate Terminal Value calculations.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Commodity & Real Estate Finance Models", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Center the title
        self.scrollable_frame.grid_columnconfigure(1, weight=1) # Span across 2 columns

        # Variables for model selection
        self.selected_model_var = tk.StringVar(value="Select a Model")

        # Dictionary to hold frames for each model's inputs
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}
        # Dictionary to store the specific input field keys for each model
        self.model_field_keys: Dict[str, List[str]] = {}


        self._create_model_selection_widgets(self.scrollable_frame, start_row=1) # Start below the title
        self._create_all_model_input_widgets(start_row=2) # Start below model selection

        self._hide_all_input_frames() # Hide all initially

        # Override the calculate button command from BaseGUI
        self.calculate_button.config(text="Calculate Model", command=self.calculate_selected_model)
        logger.info("CommodityAndRealEstateFinanceGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Commodity Futures (Cost-of-Carry)",
            "Schwartz-Smith Two-Factor Futures",
            "Real Estate Terminal Value (Gordon Growth)"
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
        but keeps them hidden initially. These frames will be packed/unpacked dynamically.
        """
        # Using self.scrollable_frame (from BaseGUI) as the parent for model-specific frames
        parent_for_models = self.scrollable_frame

        # Commodity Futures (Cost-of-Carry)
        self.model_input_frames["Commodity Futures (Cost-of-Carry)"] = self._create_cost_of_carry_widgets(parent_for_models)
        # Position relative to the model selection frame. They will all occupy the same grid cell
        self.model_input_frames["Commodity Futures (Cost-of-Carry)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Schwartz-Smith Two-Factor Futures
        self.model_input_frames["Schwartz-Smith Two-Factor Futures"] = self._create_schwartz_smith_widgets(parent_for_models)
        self.model_input_frames["Schwartz-Smith Two-Factor Futures"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Real Estate Terminal Value (Gordon Growth)
        self.model_input_frames["Real Estate Terminal Value (Gordon Growth)"] = self._create_gordon_growth_widgets(parent_for_models)
        self.model_input_frames["Real Estate Terminal Value (Gordon Growth)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Adjust common buttons and result frame positions relative to this GUI's content in scrollable_frame
        # These are already created by BaseGUI's _create_common_widgets and placed in self.scrollable_frame
        # We just need to ensure their row is higher than any model-specific input frame.
        self.result_frame.grid(row=start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=start_row + 2, column=0, columnspan=2, pady=5)


    def _hide_all_input_frames(self):
        """Hides all model-specific input frames by packing them away."""
        for frame in self.model_input_frames.values():
            frame.grid_forget() # Use grid_forget as frames are placed with grid
        self.display_result("Select a model to view its inputs and calculate.", is_error=False) # Clear previous results/errors
        # self.clear_error_messages() # Handled by display_result now

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected model for Commodity/Real Estate: {selected_model}")
        self._hide_all_input_frames()
        if selected_model in self.model_input_frames:
            # Show the selected model's frame
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        else:
            self.display_result("Please select a valid model.", is_error=True)

    # --- Widget creation methods for each model ---

    def _create_cost_of_carry_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Commodity Futures (Cost-of-Carry) Model."""
        frame = ttk.LabelFrame(parent_frame, text="Commodity Futures (Cost-of-Carry) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = [] # To store the keys for this specific model

        row_idx = 0
        # S (Spot Price)
        self.create_input_row(frame, row_idx, "Spot Price (S):", "100.00", "Current spot price of the commodity.")
        field_keys.append(self._get_field_key_from_label("Spot Price (S):"))
        row_idx += 1

        # T (Time to Maturity)
        self.create_input_row(frame, row_idx, "Time to Maturity (T, years):", "0.50", "Time until future expiration, in years.")
        field_keys.append(self._get_field_key_from_label("Time to Maturity (T, years):"))
        row_idx += 1

        # r (Risk-free Rate)
        self.create_input_row(frame, row_idx, "Risk-free Rate (r, %):", "5.00", "Annual risk-free interest rate as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-free Rate (r, %):"))
        row_idx += 1

        # Storage Cost Rate
        self.create_input_row(frame, row_idx, "Storage Cost Rate (u, %):", "1.00", "Annual storage cost rate as a percentage of commodity value.")
        field_keys.append(self._get_field_key_from_label("Storage Cost Rate (u, %):"))
        row_idx += 1

        # Convenience Yield Rate
        self.create_input_row(frame, row_idx, "Convenience Yield (y, %):", "0.50", "Annual convenience yield as a percentage.")
        field_keys.append(self._get_field_key_from_label("Convenience Yield (y, %):"))
        row_idx += 1

        self.model_field_keys["Commodity Futures (Cost-of-Carry)"] = field_keys
        return frame

    def _create_schwartz_smith_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Schwartz-Smith Two-Factor Model."""
        frame = ttk.LabelFrame(parent_frame, text="Schwartz-Smith Two-Factor Futures Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # S (Current Spot Price)
        self.create_input_row(frame, row_idx, "Current Spot Price (S):", "100.00", "Current market price of the commodity.")
        field_keys.append(self._get_field_key_from_label("Current Spot Price (S):"))
        row_idx += 1

        # current_long_term_factor_Z (log units)
        self.create_input_row(frame, row_idx, "Current Long-Term Factor (Zt, log units):", "0.00", "Current value of the long-term price factor (logarithmic).")
        field_keys.append(self._get_field_key_from_label("Current Long-Term Factor (Zt, log units):"))
        row_idx += 1

        # time_to_maturity
        self.create_input_row(frame, row_idx, "Time to Maturity (T, years):", "0.50", "Time until future expiration, in years.")
        field_keys.append(self._get_field_key_from_label("Time to Maturity (T, years):"))
        row_idx += 1

        # risk_free_rate
        self.create_input_row(frame, row_idx, "Risk-free Rate (r, %):", "5.00", "Annual risk-free interest rate as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-free Rate (r, %):"))
        row_idx += 1

        # kappa
        self.create_input_row(frame, row_idx, "Mean Reversion Rate (κ):", "0.50", "Rate at which the spot price reverts to its long-term mean.")
        field_keys.append(self._get_field_key_from_label("Mean Reversion Rate (κ):"))
        row_idx += 1

        # sigma_X
        self.create_input_row(frame, row_idx, "Short-Term Volatility (σ_X, %):", "20.00", "Volatility of the short-term deviation from the long-term price.")
        field_keys.append(self._get_field_key_from_label("Short-Term Volatility (σ_X, %):"))
        row_idx += 1

        # sigma_Zeta
        self.create_input_row(frame, row_idx, "Long-Term Volatility (σ_ζ, %):", "15.00", "Volatility of the long-term equilibrium price.")
        field_keys.append(self._get_field_key_from_label("Long-Term Volatility (σ_ζ, %):"))
        row_idx += 1

        # rho
        self.create_input_row(frame, row_idx, "Correlation (ρ, -1 to 1):", "0.50", "Correlation between the short-term and long-term factors.")
        field_keys.append(self._get_field_key_from_label("Correlation (ρ, -1 to 1):"))
        row_idx += 1

        self.model_field_keys["Schwartz-Smith Two-Factor Futures"] = field_keys
        return frame

    def _create_gordon_growth_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Real Estate Terminal Value (Gordon Growth) Model."""
        frame = ttk.LabelFrame(parent_frame, text="Real Estate Terminal Value (Gordon Growth) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # net_operating_income_next_period
        self.create_input_row(frame, row_idx, "NOI for Next Period (NOI_n+1):", "100000.00", "Net Operating Income expected for the next period.")
        field_keys.append(self._get_field_key_from_label("NOI for Next Period (NOI_n+1):"))
        row_idx += 1

        # exit_cap_rate
        self.create_input_row(frame, row_idx, "Exit Cap Rate (%, CapEx):", "6.00", "Capitalization rate used to convert NOI into value upon exit.")
        field_keys.append(self._get_field_key_from_label("Exit Cap Rate (%, CapEx):"))
        row_idx += 1

        # long_term_growth_rate
        self.create_input_row(frame, row_idx, "Long-Term Growth Rate (%, g):", "2.00", "Expected perpetual growth rate of NOI after the forecast period.")
        field_keys.append(self._get_field_key_from_label("Long-Term Growth Rate (%, g):"))
        row_idx += 1

        self.model_field_keys["Real Estate Terminal Value (Gordon Growth)"] = field_keys
        return frame

    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Replicates the field key generation logic from BaseGUI's create_input_row.
        """
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    # --- Calculation Logic ---

    def calculate_selected_model(self):
        """
        Retrieves inputs based on the selected model, validates them using BaseGUI's methods,
        performs the calculation, and displays the result.
        """
        self.display_result("Calculating...", is_error=False) # Clear previous messages and show loading
        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Model":
            self.display_result("Please select a model to calculate.", is_error=True)
            return

        # Get the field keys specific to the selected model
        field_keys_for_model = self.model_field_keys.get(selected_model)
        if not field_keys_for_model:
            self.display_result("Internal error: Field keys not found for selected model.", is_error=True)
            logger.error(f"Field keys missing for model: {selected_model}")
            return

        validated_inputs = {}
        all_valid = True

        # Retrieve and validate inputs using BaseGUI's methods
        for key in field_keys_for_model:
            value_str = self.get_input_value(key)
            field_name_for_display = key.replace('_', ' ').title() # Revert key to display name if needed

            is_percentage_field = False
            validation_type = 'numeric' # Default validation type

            # Determine validation type based on field key or model
            if selected_model == "Commodity Futures (Cost-of-Carry)":
                if key in ["risk_free_rate_r", "storage_cost_rate_u", "convenience_yield_y"]:
                    validation_type = 'percentage'
                    is_percentage_field = True
                elif key in ["spot_price_s", "time_to_maturity_t_years"]:
                    validation_type = 'positive_numeric'
                else:
                    validation_type = 'numeric' # Fallback for new key parsing behavior

            elif selected_model == "Schwartz-Smith Two-Factor Futures":
                if key in ["risk_free_rate_r", "short_term_volatility_σ_x", "long_term_volatility_σ_ζ"]:
                    validation_type = 'percentage'
                    is_percentage_field = True
                elif key in ["correlation_ρ_-1_to_1"]:
                    # Specific numeric range check for correlation
                    is_valid, processed_value = self.validate_input(value_str, 'numeric', field_name_for_display)
                    if is_valid and not (-1.0 <= processed_value <= 1.0):
                        is_valid, processed_value = False, f"'{field_name_for_display}' must be between -1 and 1."
                    if not is_valid:
                        self.display_result(processed_value, is_error=True)
                        all_valid = False
                        break
                    validated_inputs[key] = processed_value
                    continue # Skip general validation below for this field
                else:
                    validation_type = 'positive_numeric' # Most other fields
            
            elif selected_model == "Real Estate Terminal Value (Gordon Growth)":
                if key in ["exit_cap_rate_capex", "long_term_growth_rate_g"]:
                    validation_type = 'percentage'
                    is_percentage_field = True
                elif key in ["noi_for_next_period_noi_n_1"]:
                    validation_type = 'non_negative_numeric' # NOI can be zero in some cases
                else:
                    validation_type = 'numeric'

            # Perform validation using BaseGUI's validate_input
            is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)

            if not is_valid:
                self.display_result(processed_value, is_error=True) # processed_value is the error message
                all_valid = False
                break
            
            # Manually convert percentage if BaseGUI's validate_input does not automatically divide by 100
            # Your BaseGUI's validate_percentage_input returns the raw number, not divided by 100.
            # So, we need to divide it here.
            if is_percentage_field:
                processed_value /= 100.0

            validated_inputs[key] = processed_value

        if not all_valid:
            return # Stop if any input is invalid

        try:
            if selected_model == "Commodity Futures (Cost-of-Carry)":
                S = validated_inputs[self._get_field_key_from_label("Spot Price (S):")]
                T = validated_inputs[self._get_field_key_from_label("Time to Maturity (T, years):")]
                r = validated_inputs[self._get_field_key_from_label("Risk-free Rate (r, %):")]
                storage_cost_rate = validated_inputs[self._get_field_key_from_label("Storage Cost Rate (u, %):")]
                convenience_yield_rate = validated_inputs[self._get_field_key_from_label("Convenience Yield (y, %):")]

                futures_price = calculate_commodity_futures_price_cost_of_carry(
                    S=S, T=T, r=r,
                    storage_cost_rate=storage_cost_rate,
                    convenience_yield_rate=convenience_yield_rate
                )
                self.display_result(f"Calculated Futures Price (Cost-of-Carry): {self.format_currency_output(futures_price)}")

            elif selected_model == "Schwartz-Smith Two-Factor Futures":
                S = validated_inputs[self._get_field_key_from_label("Current Spot Price (S):")]
                current_long_term_factor_Z = validated_inputs[self._get_field_key_from_label("Current Long-Term Factor (Zt, log units):")]
                time_to_maturity = validated_inputs[self._get_field_key_from_label("Time to Maturity (T, years):")]
                risk_free_rate = validated_inputs[self._get_field_key_from_label("Risk-free Rate (r, %):")]
                kappa = validated_inputs[self._get_field_key_from_label("Mean Reversion Rate (κ):")]
                sigma_X = validated_inputs[self._get_field_key_from_label("Short-Term Volatility (σ_X, %):")]
                sigma_Zeta = validated_inputs[self._get_field_key_from_label("Long-Term Volatility (σ_ζ, %):")]
                rho = validated_inputs[self._get_field_key_from_label("Correlation (ρ, -1 to 1):")]

                futures_price = calculate_schwartz_smith_futures_price(
                    S=S, current_long_term_factor_Z=current_long_term_factor_Z,
                    time_to_maturity=time_to_maturity, risk_free_rate=risk_free_rate,
                    kappa=kappa, sigma_X=sigma_X, sigma_Zeta=sigma_Zeta, rho=rho
                )
                self.display_result(f"Calculated Futures Price (Schwartz-Smith): {self.format_currency_output(futures_price)}")

            elif selected_model == "Real Estate Terminal Value (Gordon Growth)":
                noi = validated_inputs[self._get_field_key_from_label("NOI for Next Period (NOI_n+1):")]
                exit_cap_rate = validated_inputs[self._get_field_key_from_label("Exit Cap Rate (%, CapEx):")]
                long_term_growth_rate = validated_inputs[self._get_field_key_from_label("Long-Term Growth Rate (%, g):")]

                # Gordon Growth model constraint: growth rate must be less than cap rate
                if long_term_growth_rate >= exit_cap_rate:
                    raise ValueError("Long-Term Growth Rate (g) must be less than Exit Cap Rate (CapEx) for the Gordon Growth model.")

                terminal_value = calculate_real_estate_terminal_value_gordon_growth(
                    net_operating_income_next_period=noi,
                    exit_cap_rate=exit_cap_rate,
                    long_term_growth_rate=long_term_growth_rate
                )
                self.display_result(f"Real Estate Terminal Value: {self.format_currency_output(terminal_value)}")

        except ValueError as e:
            logger.warning(f"Calculation error for {selected_model}: {e}")
            self.display_result(f"Input Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Calculation error (division by zero) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs like rates/cap rates.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection
        and update the UI state.
        """
        super().clear_inputs() # Clear all underlying entry widgets via BaseGUI's input_fields
        self.selected_model_var.set("Select a Model") # Reset combobox
        self._on_model_selected() # Trigger UI update to hide frames and clear messages

# Example usage (for testing CommodityAndRealEstateFinanceGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Commodity & Real Estate Finance Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x700") # Adjust size as needed

    # style = ttk.Style()
    # style.theme_use('clam')

    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    commodity_real_estate_gui = CommodityAndRealEstateFinanceGUI(test_parent_frame, controller=None)
    commodity_real_estate_gui.pack(fill="both", expand=True)

    root.mainloop()