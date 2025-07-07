# financial_calculator/gui/equity_portfolio_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, List, Callable, Union
import re # Needed for field key generation consistency

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import mathematical functions as per PROJECT_STRUCTURE.md
# From equity_valuation.py
from mathematical_functions.equity_valuation import (
    gordon_growth_model
)
# From portfolio_management.py
from mathematical_functions.portfolio_management import (
    calculate_capm_return,
    fama_french_3_factor_expected_return,
    fama_french_5_factor_expected_return,
    calculate_sharpe_ratio
)

# Import constants (for formatting, if needed in the future directly)
from config import DEFAULT_WINDOW_WIDTH # for example usage

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class EquityPortfolioGUI(BaseGUI):
    """
    GUI module for Equity Valuation and Portfolio Management calculations.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Equity & Portfolio Models", font=("Arial", 14, "bold"))
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
        logger.info("EquityPortfolioGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Gordon Growth Model (Stock Price)",
            "CAPM Expected Return",
            "Fama-French 3-Factor Expected Return",
            "Fama-French 5-Factor Expected Return",
            "Sharpe Ratio"
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

        # Gordon Growth Model Inputs
        self.model_input_frames["Gordon Growth Model (Stock Price)"] = self._create_gordon_growth_widgets(parent_for_models)
        self.model_input_frames["Gordon Growth Model (Stock Price)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # CAPM Expected Return Inputs
        self.model_input_frames["CAPM Expected Return"] = self._create_capm_widgets(parent_for_models)
        self.model_input_frames["CAPM Expected Return"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Fama-French 3-Factor Expected Return Inputs
        self.model_input_frames["Fama-French 3-Factor Expected Return"] = self._create_ff3_widgets(parent_for_models)
        self.model_input_frames["Fama-French 3-Factor Expected Return"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Fama-French 5-Factor Expected Return Inputs
        self.model_input_frames["Fama-French 5-Factor Expected Return"] = self._create_ff5_widgets(parent_for_models)
        self.model_input_frames["Fama-French 5-Factor Expected Return"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Sharpe Ratio Inputs
        self.model_input_frames["Sharpe Ratio"] = self._create_sharpe_ratio_widgets(parent_for_models)
        self.model_input_frames["Sharpe Ratio"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Adjust common buttons and result frame positions relative to this GUI's grid
        self.result_frame.grid(row=start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=start_row + 2, column=0, columnspan=2, pady=5)


    def _hide_all_input_frames(self):
        """Hides all model-specific input frames."""
        for frame in self.model_input_frames.values():
            frame.grid_forget()
        self.display_result("Select a model to view its inputs and calculate.", is_error=False)

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected model for Equity/Portfolio: {selected_model}")
        self._hide_all_input_frames()
        if selected_model in self.model_input_frames:
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        else:
            self.display_result("Please select a valid model.", is_error=True)

    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Replicates the field key generation logic from BaseGUI's create_input_row.
        """
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    # --- Widget creation methods for each model ---

    def _create_gordon_growth_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Gordon Growth Model."""
        frame = ttk.LabelFrame(parent_frame, text="Gordon Growth Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Next Year's Dividend (D1):", "1.00", "Expected dividend per share in the next period.")
        field_keys.append(self._get_field_key_from_label("Next Year's Dividend (D1):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Required Rate of Return (r, %):", "10.00", "The required rate of return for the equity, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Required Rate of Return (r, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Constant Growth Rate (g, %):", "5.00", "The constant growth rate of dividends, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Constant Growth Rate (g, %):"))
        row_idx += 1

        self.model_field_keys["Gordon Growth Model (Stock Price)"] = field_keys
        return frame

    def _create_capm_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the CAPM Expected Return."""
        frame = ttk.LabelFrame(parent_frame, text="CAPM Expected Return Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Risk-Free Rate (CAPM, %):", "3.00", "The risk-free rate of return, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Market Return (CAPM, %):", "8.00", "The expected return of the overall market, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Market Return (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Beta (CAPM):", "1.20", "A measure of the asset's systematic risk relative to the market.")
        field_keys.append(self._get_field_key_from_label("Beta (CAPM):"))
        row_idx += 1

        self.model_field_keys["CAPM Expected Return"] = field_keys
        return frame

    def _create_ff3_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Fama-French 3-Factor Expected Return."""
        frame = ttk.LabelFrame(parent_frame, text="Fama-French 3-Factor Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # Inherits from CAPM, so need those fields too, plus FF3 specific ones
        # Using specific keys to ensure they are looked up correctly by _get_field_key_from_label
        self.create_input_row(frame, row_idx, "Risk-Free Rate (CAPM, %):", "3.00", "The risk-free rate of return, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Market Return (CAPM, %):", "8.00", "The expected return of the overall market, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Market Return (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Beta (CAPM):", "1.20", "A measure of the asset's systematic risk relative to the market.")
        field_keys.append(self._get_field_key_from_label("Beta (CAPM):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "SMB Factor Return (FF3, %):", "1.50", "Return of the Small Minus Big (SMB) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("SMB Factor Return (FF3, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "HML Factor Return (FF3, %):", "2.00", "Return of the High Minus Low (HML) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("HML Factor Return (FF3, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "SMB Beta (FF3):", "0.30", "Sensitivity to the SMB factor.")
        field_keys.append(self._get_field_key_from_label("SMB Beta (FF3):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "HML Beta (FF3):", "0.40", "Sensitivity to the HML factor.")
        field_keys.append(self._get_field_key_from_label("HML Beta (FF3):"))
        row_idx += 1

        self.model_field_keys["Fama-French 3-Factor Expected Return"] = field_keys
        return frame

    def _create_ff5_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Fama-French 5-Factor Expected Return."""
        frame = ttk.LabelFrame(parent_frame, text="Fama-French 5-Factor Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # Inherits from FF3, so need those fields too, plus FF5 specific ones
        self.create_input_row(frame, row_idx, "Risk-Free Rate (CAPM, %):", "3.00", "The risk-free rate of return, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Market Return (CAPM, %):", "8.00", "The expected return of the overall market, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Market Return (CAPM, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Beta (CAPM):", "1.20", "A measure of the asset's systematic risk relative to the market.")
        field_keys.append(self._get_field_key_from_label("Beta (CAPM):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "SMB Factor Return (FF3, %):", "1.50", "Return of the Small Minus Big (SMB) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("SMB Factor Return (FF3, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "HML Factor Return (FF3, %):", "2.00", "Return of the High Minus Low (HML) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("HML Factor Return (FF3, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "SMB Beta (FF3):", "0.30", "Sensitivity to the SMB factor.")
        field_keys.append(self._get_field_key_from_label("SMB Beta (FF3):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "HML Beta (FF3):", "0.40", "Sensitivity to the HML factor.")
        field_keys.append(self._get_field_key_from_label("HML Beta (FF3):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "RMW Factor Return (FF5, %):", "0.80", "Return of the Robust Minus Weak (RMW) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("RMW Factor Return (FF5, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "CMA Factor Return (FF5, %):", "1.20", "Return of the Conservative Minus Aggressive (CMA) factor, as a percentage.")
        field_keys.append(self._get_field_key_from_label("CMA Factor Return (FF5, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "RMW Beta (FF5):", "0.20", "Sensitivity to the RMW factor.")
        field_keys.append(self._get_field_key_from_label("RMW Beta (FF5):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "CMA Beta (FF5):", "0.15", "Sensitivity to the CMA factor.")
        field_keys.append(self._get_field_key_from_label("CMA Beta (FF5):"))
        row_idx += 1

        self.model_field_keys["Fama-French 5-Factor Expected Return"] = field_keys
        return frame

    def _create_sharpe_ratio_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Sharpe Ratio calculation."""
        frame = ttk.LabelFrame(parent_frame, text="Sharpe Ratio Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        self.create_input_row(frame, row_idx, "Portfolio Return (Sharpe, %):", "12.00", "The total return of the portfolio, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Portfolio Return (Sharpe, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Portfolio Std Dev (Sharpe, %):", "15.00", "The standard deviation of the portfolio's returns, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Portfolio Std Dev (Sharpe, %):"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Risk-Free Rate (Sharpe, %):", "3.00", "The risk-free rate of return for Sharpe Ratio, as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-Free Rate (Sharpe, %):"))
        row_idx += 1

        self.model_field_keys["Sharpe Ratio"] = field_keys
        return frame

    # --- Calculation Logic ---

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

        field_keys_for_model = self.model_field_keys.get(selected_model)
        if not field_keys_for_model:
            self.display_result("Internal error: Field keys not found for selected model.", is_error=True)
            logger.error(f"Field keys missing for model: {selected_model}")
            return

        validated_inputs = {}
        all_valid = True

        for key in field_keys_for_model:
            value_str = self.get_input_value(key)
            field_name_for_display = key.replace('_', ' ').title()

            # Initialize for each key iteration
            is_percentage_field = False
            validation_type = 'numeric' # Default

            # Determine specific validation type and if it's a percentage
            if selected_model == "Gordon Growth Model (Stock Price)":
                if key in [self._get_field_key_from_label("Next Year's Dividend (D1):")]:
                    validation_type = 'non_negative_numeric' # Dividend can be 0 or positive
                elif key in [self._get_field_key_from_label("Required Rate of Return (r, %):"),
                             self._get_field_key_from_label("Constant Growth Rate (g, %):")]:
                    validation_type = 'numeric' # Can be negative, but validate as percent
                    is_percentage_field = True

            elif selected_model == "CAPM Expected Return":
                if key in [self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"),
                           self._get_field_key_from_label("Market Return (CAPM, %):")]:
                    validation_type = 'numeric'
                    is_percentage_field = True
                elif key == self._get_field_key_from_label("Beta (CAPM):"):
                    validation_type = 'numeric' # Beta can be positive or negative

            elif selected_model == "Fama-French 3-Factor Expected Return":
                # CAPM related inputs
                if key in [self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"),
                           self._get_field_key_from_label("Market Return (CAPM, %):"),
                           self._get_field_key_from_label("SMB Factor Return (FF3, %):"),
                           self._get_field_key_from_label("HML Factor Return (FF3, %):")]:
                    validation_type = 'numeric'
                    is_percentage_field = True
                elif key in [self._get_field_key_from_label("Beta (CAPM):"),
                             self._get_field_key_from_label("SMB Beta (FF3):"),
                             self._get_field_key_from_label("HML Beta (FF3):")]:
                    validation_type = 'numeric'

            elif selected_model == "Fama-French 5-Factor Expected Return":
                # FF3 related inputs
                if key in [self._get_field_key_from_label("Risk-Free Rate (CAPM, %):"),
                           self._get_field_key_from_label("Market Return (CAPM, %):"),
                           self._get_field_key_from_label("SMB Factor Return (FF3, %):"),
                           self._get_field_key_from_label("HML Factor Return (FF3, %):"),
                           self._get_field_key_from_label("RMW Factor Return (FF5, %):"),
                           self._get_field_key_from_label("CMA Factor Return (FF5, %):")]:
                    validation_type = 'numeric'
                    is_percentage_field = True
                elif key in [self._get_field_key_from_label("Beta (CAPM):"),
                             self._get_field_key_from_label("SMB Beta (FF3):"),
                             self._get_field_key_from_label("HML Beta (FF3):"),
                             self._get_field_key_from_label("RMW Beta (FF5):"),
                             self._get_field_key_from_label("CMA Beta (FF5):")]:
                    validation_type = 'numeric'

            elif selected_model == "Sharpe Ratio":
                if key in [self._get_field_key_from_label("Portfolio Return (Sharpe, %):"),
                           self._get_field_key_from_label("Risk-Free Rate (Sharpe, %):")]:
                    validation_type = 'numeric'
                    is_percentage_field = True
                elif key == self._get_field_key_from_label("Portfolio Std Dev (Sharpe, %):"):
                    validation_type = 'positive_numeric' # Std dev must be positive
                    is_percentage_field = True

            is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)

            if not is_valid:
                self.display_result(processed_value, is_error=True)
                all_valid = False
                break

            if is_percentage_field:
                processed_value /= 100.0

            validated_inputs[key] = processed_value

        if not all_valid:
            return

        try:
            if selected_model == "Gordon Growth Model (Stock Price)":
                d1 = validated_inputs[self._get_field_key_from_label("Next Year's Dividend (D1):")]
                r_gg = validated_inputs[self._get_field_key_from_label("Required Rate of Return (r, %):")]
                g_gg = validated_inputs[self._get_field_key_from_label("Constant Growth Rate (g, %):")]

                if r_gg <= g_gg:
                    self.display_result("Required Rate of Return (r) must be greater than Growth Rate (g) for Gordon Growth Model.", is_error=True)
                    return
                
                result = gordon_growth_model(d1, r_gg, g_gg)
                self.display_result(f"Stock Price (Gordon Growth): {self.format_currency_output(result)}")

            elif selected_model == "CAPM Expected Return":
                rf_capm = validated_inputs[self._get_field_key_from_label("Risk-Free Rate (CAPM, %):")]
                rm_capm = validated_inputs[self._get_field_key_from_label("Market Return (CAPM, %):")]
                beta_capm = validated_inputs[self._get_field_key_from_label("Beta (CAPM):")]
                
                market_risk_premium = rm_capm - rf_capm
                
                result_decimal = calculate_capm_return(rf_capm, market_risk_premium, beta_capm)
                self.display_result(f"CAPM Expected Return: {self.format_percentage_output(result_decimal)}")

            elif selected_model == "Fama-French 3-Factor Expected Return":
                rf_capm = validated_inputs[self._get_field_key_from_label("Risk-Free Rate (CAPM, %):")]
                rm_capm = validated_inputs[self._get_field_key_from_label("Market Return (CAPM, %):")]
                beta_capm = validated_inputs[self._get_field_key_from_label("Beta (CAPM):")]
                smb_ret = validated_inputs[self._get_field_key_from_label("SMB Factor Return (FF3, %):")]
                hml_ret = validated_inputs[self._get_field_key_from_label("HML Factor Return (FF3, %):")]
                smb_beta = validated_inputs[self._get_field_key_from_label("SMB Beta (FF3):")]
                hml_beta = validated_inputs[self._get_field_key_from_label("HML Beta (FF3):")]
                
                market_excess_return = rm_capm - rf_capm

                result_decimal = fama_french_3_factor_expected_return(
                    rf_capm, beta_capm, smb_beta, hml_beta,
                    market_excess_return, smb_ret, hml_ret
                )
                self.display_result(f"Fama-French 3-Factor Expected Return: {self.format_percentage_output(result_decimal)}")

            elif selected_model == "Fama-French 5-Factor Expected Return":
                rf_capm = validated_inputs[self._get_field_key_from_label("Risk-Free Rate (CAPM, %):")]
                rm_capm = validated_inputs[self._get_field_key_from_label("Market Return (CAPM, %):")]
                beta_capm = validated_inputs[self._get_field_key_from_label("Beta (CAPM):")]
                smb_ret = validated_inputs[self._get_field_key_from_label("SMB Factor Return (FF3, %):")]
                hml_ret = validated_inputs[self._get_field_key_from_label("HML Factor Return (FF3, %):")]
                rmw_ret = validated_inputs[self._get_field_key_from_label("RMW Factor Return (FF5, %):")]
                cma_ret = validated_inputs[self._get_field_key_from_label("CMA Factor Return (FF5, %):")]
                smb_beta = validated_inputs[self._get_field_key_from_label("SMB Beta (FF3):")]
                hml_beta = validated_inputs[self._get_field_key_from_label("HML Beta (FF3):")]
                rmw_beta = validated_inputs[self._get_field_key_from_label("RMW Beta (FF5):")]
                cma_beta = validated_inputs[self._get_field_key_from_label("CMA Beta (FF5):")]
                
                market_excess_return = rm_capm - rf_capm

                result_decimal = fama_french_5_factor_expected_return(
                    rf_capm, beta_capm, smb_beta, hml_beta, rmw_beta, cma_beta,
                    market_excess_return, smb_ret, hml_ret, rmw_ret, cma_ret
                )
                self.display_result(f"Fama-French 5-Factor Expected Return: {self.format_percentage_output(result_decimal)}")

            elif selected_model == "Sharpe Ratio":
                port_ret_sharpe = validated_inputs[self._get_field_key_from_label("Portfolio Return (Sharpe, %):")]
                port_std_dev_sharpe = validated_inputs[self._get_field_key_from_label("Portfolio Std Dev (Sharpe, %):")]
                rf_sharpe = validated_inputs[self._get_field_key_from_label("Risk-Free Rate (Sharpe, %):")]
                
                if port_std_dev_sharpe <= 0: # Ensure positive standard deviation
                    self.display_result("Portfolio Standard Deviation must be positive for Sharpe Ratio calculation.", is_error=True)
                    return

                result = calculate_sharpe_ratio(port_ret_sharpe, rf_sharpe, port_std_dev_sharpe)
                self.display_result(f"Sharpe Ratio: {self.format_number_output(result, 4)}")

        except ValueError as e:
            logger.error(f"Equity/Portfolio Calculation Error (ValueError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Equity/Portfolio Calculation Error (ZeroDivisionError) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs.", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Equity/Portfolio calculation for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection
        and update the UI state.
        """
        super().clear_inputs() # Clear all underlying entry widgets via BaseGUI's input_fields
        self.selected_model_var.set("Select a Model") # Reset combobox
        self._on_model_selected() # Trigger UI update to hide frames and clear messages

# Example usage (for testing EquityPortfolioGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Equity & Portfolio Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x800") # Adjust size as needed

    # style = ttk.Style()
    # style.theme_use('clam')

    # For isolation testing, a simple frame acts as the parent
    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    equity_portfolio_gui = EquityPortfolioGUI(test_parent_frame, controller=None)
    equity_portfolio_gui.pack(fill="both", expand=True)

    root.mainloop()