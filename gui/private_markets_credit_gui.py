# financial_calculator/gui/private_markets_credit_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, List, Callable, Union
import re # Needed for field key generation consistency

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import mathematical functions as per the agreed structure
from mathematical_functions.credit_risk_advanced import calculate_merton_model_credit_risk
from mathematical_functions.private_markets_valuation import (
    calculate_illiquidity_discount_option_model,
    simulate_private_equity_valuation_monte_carlo
)

# Import constants (for formatting)
from config import (
    DEFAULT_DECIMAL_PLACES_CURRENCY, DEFAULT_DECIMAL_PLACES_PERCENTAGE,
    DEFAULT_DECIMAL_PLACES_GENERAL, DEFAULT_WINDOW_WIDTH
)

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PrivateMarketsAndCreditRiskGUI(BaseGUI):
    """
    GUI module for Merton Credit Risk, Illiquidity Discount, and Private Equity Monte Carlo Valuation.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        # Create a specific title label for this GUI, packed into the scrollable frame
        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Private Markets & Credit Risk Models", font=("Arial", 14, "bold"))
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
        logger.info("PrivateMarketsAndCreditRiskGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Merton Credit Risk Model",
            "Illiquidity Discount (Option Model)",
            "Private Equity Monte Carlo Valuation"
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
        parent_for_models = self.scrollable_frame # Place directly in scrollable frame below selection

        # Merton Credit Risk Model
        self.model_input_frames["Merton Credit Risk Model"] = self._create_merton_widgets(parent_for_models)
        self.model_input_frames["Merton Credit Risk Model"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Illiquidity Discount (Option Model)
        self.model_input_frames["Illiquidity Discount (Option Model)"] = self._create_illiquidity_widgets(parent_for_models)
        self.model_input_frames["Illiquidity Discount (Option Model)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Private Equity Monte Carlo Valuation
        self.model_input_frames["Private Equity Monte Carlo Valuation"] = self._create_pe_monte_carlo_widgets(parent_for_models)
        self.model_input_frames["Private Equity Monte Carlo Valuation"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Adjust common buttons and result frame positions relative to this GUI's grid
        # These are handled by BaseGUI and their position within scrollable_frame is determined by BaseGUI.
        # We just need to make sure their grid row is after all model-specific input frames.
        self.result_frame.grid(row=start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=start_row + 2, column=0, columnspan=2, pady=5)


    def _hide_all_input_frames(self):
        """Hides all model-specific input frames by packing them away."""
        for frame in self.model_input_frames.values():
            frame.grid_forget() # Use grid_forget as frames are placed with grid
        self.display_result("Select a model to view its inputs and calculate.", is_error=False) # Clear previous results/errors

    def _on_model_selected(self, event=None):
        """Callback when a model is selected from the combobox."""
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected model for Private Markets/Credit Risk: {selected_model}")
        self._hide_all_input_frames()
        if selected_model in self.model_input_frames:
            # Show the selected model's frame at the fixed content row
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        else:
            self.display_result("Please select a valid model.", is_error=True)

    # --- Widget creation methods for each model ---

    def _create_merton_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Merton Credit Risk Model."""
        frame = ttk.LabelFrame(parent_frame, text="Merton Credit Risk Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # E (Equity Value)
        self.create_input_row(frame, row_idx, "Equity Value (E):", "1000.00", "Current market value of the company's equity.")
        field_keys.append(self._get_field_key_from_label("Equity Value (E):"))
        row_idx += 1

        # sigma_E (Equity Volatility)
        self.create_input_row(frame, row_idx, "Equity Volatility (σ_E, %):", "30.00", "Annualized volatility of the company's equity as a percentage.")
        field_keys.append(self._get_field_key_from_label("Equity Volatility (σ_E, %):"))
        row_idx += 1

        # D (Face Value of Debt)
        self.create_input_row(frame, row_idx, "Face Value of Debt (D):", "500.00", "Total face value of debt maturing at time T.")
        field_keys.append(self._get_field_key_from_label("Face Value of Debt (D):"))
        row_idx += 1

        # T (Time to Maturity)
        self.create_input_row(frame, row_idx, "Time to Maturity (T, years):", "1.00", "Time until debt maturity, in years.")
        field_keys.append(self._get_field_key_from_label("Time to Maturity (T, years):"))
        row_idx += 1

        # r (Risk-free Rate)
        self.create_input_row(frame, row_idx, "Risk-free Rate (r, %):", "5.00", "Annual risk-free interest rate as a percentage.")
        field_keys.append(self._get_field_key_from_label("Risk-free Rate (r, %):"))
        row_idx += 1

        # Initial V Guess (Optional)
        self.create_input_row(frame, row_idx, "Initial Asset Value Guess (Optional):", "", "An optional initial guess for the company's asset value for iterative calculation.")
        field_keys.append(self._get_field_key_from_label("Initial Asset Value Guess (Optional):"))
        row_idx += 1

        # Initial Sigma V Guess (Optional)
        self.create_input_row(frame, row_idx, "Initial Asset Volatility Guess (Optional, %):", "", "An optional initial guess for the company's asset volatility.")
        field_keys.append(self._get_field_key_from_label("Initial Asset Volatility Guess (Optional, %):"))
        row_idx += 1

        self.model_field_keys["Merton Credit Risk Model"] = field_keys
        return frame

    def _create_illiquidity_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Illiquidity Discount (Option Model)."""
        frame = ttk.LabelFrame(parent_frame, text="Illiquidity Discount (Option Model) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # asset_value
        self.create_input_row(frame, row_idx, "Asset Value:", "100.00", "Current value of the illiquid asset.")
        field_keys.append(self._get_field_key_from_label("Asset Value:"))
        row_idx += 1

        # liquidation_cost_pct
        self.create_input_row(frame, row_idx, "Liquidation Cost (%, e.g., 10 for 10%):", "10.00", "Cost incurred as a percentage of asset value to liquidate the asset quickly.")
        field_keys.append(self._get_field_key_from_label("Liquidation Cost (%, e.g., 10 for 10%):"))
        row_idx += 1

        # holding_period
        self.create_input_row(frame, row_idx, "Holding Period (years):", "1.00", "Expected period for which the asset will be held before liquidation.")
        field_keys.append(self._get_field_key_from_label("Holding Period (years):"))
        row_idx += 1

        # volatility
        self.create_input_row(frame, row_idx, "Asset Volatility (%, annualized):", "20.00", "Annualized volatility of the underlying asset's value.")
        field_keys.append(self._get_field_key_from_label("Asset Volatility (%, annualized):"))
        row_idx += 1

        # risk_free_rate
        self.create_input_row(frame, row_idx, "Risk-free Rate (%, continuous):", "5.00", "Annual continuous risk-free interest rate.")
        field_keys.append(self._get_field_key_from_label("Risk-free Rate (%, continuous):"))
        row_idx += 1

        # g_spread (Optional)
        self.create_input_row(frame, row_idx, "G-Spread (%, optional):", "", "Optional spread above the risk-free rate reflecting specific risk.")
        field_keys.append(self._get_field_key_from_label("G-Spread (%, optional):"))
        row_idx += 1

        self.model_field_keys["Illiquidity Discount (Option Model)"] = field_keys
        return frame

    def _create_pe_monte_carlo_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for the Private Equity Monte Carlo Valuation Model."""
        frame = ttk.LabelFrame(parent_frame, text="Private Equity Monte Carlo Valuation Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0

        # base_free_cash_flows (List input)
        self.create_input_row(frame, row_idx, "Base Free Cash Flows (comma-separated):", "10,20,30,40,50", "Forecasted unlevered free cash flows for each year.")
        field_keys.append(self._get_field_key_from_label("Base Free Cash Flows (comma-separated):"))
        row_idx += 1

        # terminal_value_growth_rate_mean
        self.create_input_row(frame, row_idx, "TV Growth Rate Mean (%, μ_g):", "2.00", "Mean of the normal distribution for terminal value growth rate.")
        field_keys.append(self._get_field_key_from_label("TV Growth Rate Mean (%, μ_g):"))
        row_idx += 1

        # terminal_value_growth_rate_std
        self.create_input_row(frame, row_idx, "TV Growth Rate Std Dev (%, σ_g):", "1.00", "Standard deviation of the normal distribution for terminal value growth rate.")
        field_keys.append(self._get_field_key_from_label("TV Growth Rate Std Dev (%, σ_g):"))
        row_idx += 1

        # discount_rate_mean
        self.create_input_row(frame, row_idx, "Discount Rate Mean (%, μ_DR):", "10.00", "Mean of the normal distribution for the discount rate (WACC).")
        field_keys.append(self._get_field_key_from_label("Discount Rate Mean (%, μ_DR):"))
        row_idx += 1

        # discount_rate_std
        self.create_input_row(frame, row_idx, "Discount Rate Std Dev (%, σ_DR):", "2.00", "Standard deviation of the normal distribution for the discount rate.")
        field_keys.append(self._get_field_key_from_label("Discount Rate Std Dev (%, σ_DR):"))
        row_idx += 1

        # exit_multiple_mean
        self.create_input_row(frame, row_idx, "Exit Multiple Mean (μ_EM):", "8.00", "Mean of the normal distribution for the exit multiple (e.g., EV/EBITDA).")
        field_keys.append(self._get_field_key_from_label("Exit Multiple Mean (μ_EM):"))
        row_idx += 1

        # exit_multiple_std
        self.create_input_row(frame, row_idx, "Exit Multiple Std Dev (σ_EM):", "1.00", "Standard deviation of the normal distribution for the exit multiple.")
        field_keys.append(self._get_field_key_from_label("Exit Multiple Std Dev (σ_EM):"))
        row_idx += 1

        # num_simulations
        self.create_input_row(frame, row_idx, "Number of Simulations:", "10000", "Number of Monte Carlo simulation iterations.")
        field_keys.append(self._get_field_key_from_label("Number of Simulations:"))
        row_idx += 1

        # exit_year
        self.create_input_row(frame, row_idx, "Exit Year (e.g., 5 for Year 5):", "5", "The year in which the company is assumed to be exited.")
        field_keys.append(self._get_field_key_from_label("Exit Year (e.g., 5 for Year 5):"))
        row_idx += 1

        # seed (Optional)
        self.create_input_row(frame, row_idx, "Random Seed (Optional):", "", "Optional seed for reproducibility of Monte Carlo simulations.")
        field_keys.append(self._get_field_key_from_label("Random Seed (Optional):"))
        row_idx += 1

        self.model_field_keys["Private Equity Monte Carlo Valuation"] = field_keys
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

            is_optional = False
            if key in [
                self._get_field_key_from_label("Initial Asset Value Guess (Optional):"),
                self._get_field_key_from_label("Initial Asset Volatility Guess (Optional, %):"),
                self._get_field_key_from_label("G-Spread (%, optional):"),
                self._get_field_key_from_label("Random Seed (Optional):")
            ]:
                is_optional = True

            if is_optional and not value_str.strip():
                validated_inputs[key] = None
                continue

            # --- FIX STARTS HERE ---
            # Always initialize is_percentage_field before the conditional blocks
            is_percentage_field = False
            validation_type = 'numeric' # Default validation type, can be overridden below

            # Special handling for list input for Monte Carlo
            if key == self._get_field_key_from_label("Base Free Cash Flows (comma-separated):"):
                is_valid, processed_value = self.validate_input_list(value_str, 'numeric', field_name_for_display)
            else:
                # Determine specific validation type and if it's a percentage
                if selected_model == "Merton Credit Risk Model":
                    if key in [self._get_field_key_from_label("Equity Volatility (σ_E, %):"),
                               self._get_field_key_from_label("Risk-free Rate (r, %):"),
                               self._get_field_key_from_label("Initial Asset Volatility Guess (Optional, %):")]:
                        validation_type = 'percentage'
                        is_percentage_field = True
                    elif key in [self._get_field_key_from_label("Equity Value (E):"),
                                 self._get_field_key_from_label("Face Value of Debt (D):"),
                                 self._get_field_key_from_label("Time to Maturity (T, years):")]:
                        validation_type = 'positive_numeric'
                    elif key == self._get_field_key_from_label("Initial Asset Value Guess (Optional):"):
                        validation_type = 'positive_numeric'

                elif selected_model == "Illiquidity Discount (Option Model)":
                    if key in [self._get_field_key_from_label("Liquidation Cost (%, e.g., 10 for 10%):"),
                               self._get_field_key_from_label("Asset Volatility (%, annualized):"),
                               self._get_field_key_from_label("Risk-free Rate (%, continuous):"),
                               self._get_field_key_from_label("G-Spread (%, optional):")]:
                        validation_type = 'percentage'
                        is_percentage_field = True
                    elif key in [self._get_field_key_from_label("Asset Value:"),
                                 self._get_field_key_from_label("Holding Period (years):")]:
                        validation_type = 'positive_numeric'

                elif selected_model == "Private Equity Monte Carlo Valuation":
                    if key in [self._get_field_key_from_label("TV Growth Rate Mean (%, μ_g):"),
                               self._get_field_key_from_label("TV Growth Rate Std Dev (%, σ_g):"),
                               self._get_field_key_from_label("Discount Rate Mean (%, μ_DR):"),
                               self._get_field_key_from_label("Discount Rate Std Dev (%, σ_DR):")]:
                        validation_type = 'percentage'
                        is_percentage_field = True
                    elif key in [self._get_field_key_from_label("Exit Multiple Mean (μ_EM):"),
                                 self._get_field_key_from_label("Exit Multiple Std Dev (σ_EM):")]:
                        validation_type = 'non_negative_numeric'
                    elif key == self._get_field_key_from_label("Number of Simulations:"):
                        validation_type = 'positive_integer'
                    elif key == self._get_field_key_from_label("Exit Year (e.g., 5 for Year 5):"):
                        validation_type = 'positive_integer'
                    elif key == self._get_field_key_from_label("Random Seed (Optional):"):
                        validation_type = 'numeric'
                        if not value_str.strip():
                            validated_inputs[key] = None
                            continue

                # Perform validation using BaseGUI's validate_input
                is_valid, processed_value = self.validate_input(value_str, validation_type, field_name_for_display)

            if not is_valid:
                self.display_result(processed_value, is_error=True)
                all_valid = False
                break

            if is_percentage_field:
                processed_value /= 100.0

            validated_inputs[key] = processed_value
            # --- FIX ENDS HERE ---

        if not all_valid:
            return

        try:
            if selected_model == "Merton Credit Risk Model":
                E = validated_inputs[self._get_field_key_from_label("Equity Value (E):")]
                sigma_E = validated_inputs[self._get_field_key_from_label("Equity Volatility (σ_E, %):")]
                D = validated_inputs[self._get_field_key_from_label("Face Value of Debt (D):")]
                T = validated_inputs[self._get_field_key_from_label("Time to Maturity (T, years):")]
                r = validated_inputs[self._get_field_key_from_label("Risk-free Rate (r, %):")]
                initial_V_guess = validated_inputs[self._get_field_key_from_label("Initial Asset Value Guess (Optional):")]
                initial_sigma_V_guess = validated_inputs[self._get_field_key_from_label("Initial Asset Volatility Guess (Optional, %):")]

                results = calculate_merton_model_credit_risk(
                    E=E, sigma_E=sigma_E, D=D, T=T, r=r,
                    initial_V_guess=initial_V_guess,
                    initial_sigma_V_guess=initial_sigma_V_guess
                )
                output_message = (
                    f"Implied Asset Value: {self.format_currency_output(results['implied_asset_value'])}\n"
                    f"Implied Asset Volatility: {self.format_percentage_output(results['implied_asset_volatility'])}\n"
                    f"Distance to Default (DtD): {self.format_number_output(results['distance_to_default'])}\n"
                    f"Probability of Default (PD): {self.format_percentage_output(results['probability_of_default'])}"
                )
                self.display_result(output_message)

            elif selected_model == "Illiquidity Discount (Option Model)":
                asset_value = validated_inputs[self._get_field_key_from_label("Asset Value:")]
                liquidation_cost_pct = validated_inputs[self._get_field_key_from_label("Liquidation Cost (%, e.g., 10 for 10%):")]
                holding_period = validated_inputs[self._get_field_key_from_label("Holding Period (years):")]
                volatility = validated_inputs[self._get_field_key_from_label("Asset Volatility (%, annualized):")]
                risk_free_rate = validated_inputs[self._get_field_key_from_label("Risk-free Rate (%, continuous):")]
                g_spread = validated_inputs[self._get_field_key_from_label("G-Spread (%, optional):")]
                # Ensure g_spread defaults to 0.0 if not provided (already None if optional and empty)
                g_spread = g_spread if g_spread is not None else 0.0

                results = calculate_illiquidity_discount_option_model(
                    asset_value=asset_value, liquidation_cost_pct=liquidation_cost_pct,
                    holding_period=holding_period, volatility=volatility,
                    risk_free_rate=risk_free_rate, g_spread=g_spread
                )
                output_message = (
                    f"Illiquidity Discount Value: {self.format_currency_output(results['illiquidity_discount_value'])}\n"
                    f"Illiquidity Discount (% of Asset Value): {self.format_percentage_output(results['illiquidity_discount_pct'])}\n"
                    f"Adjusted Asset Value: {self.format_currency_output(results['adjusted_asset_value'])}"
                )
                self.display_result(output_message)

            elif selected_model == "Private Equity Monte Carlo Valuation":
                base_free_cash_flows = validated_inputs[self._get_field_key_from_label("Base Free Cash Flows (comma-separated):")]
                terminal_value_growth_rate_mean = validated_inputs[self._get_field_key_from_label("TV Growth Rate Mean (%, μ_g):")]
                terminal_value_growth_rate_std = validated_inputs[self._get_field_key_from_label("TV Growth Rate Std Dev (%, σ_g):")]
                discount_rate_mean = validated_inputs[self._get_field_key_from_label("Discount Rate Mean (%, μ_DR):")]
                discount_rate_std = validated_inputs[self._get_field_key_from_label("Discount Rate Std Dev (%, σ_DR):")]
                exit_multiple_mean = validated_inputs[self._get_field_key_from_label("Exit Multiple Mean (μ_EM):")]
                exit_multiple_std = validated_inputs[self._get_field_key_from_label("Exit Multiple Std Dev (σ_EM):")]
                num_simulations = int(validated_inputs[self._get_field_key_from_label("Number of Simulations:")])
                exit_year = int(validated_inputs[self._get_field_key_from_label("Exit Year (e.g., 5 for Year 5):")])
                seed = validated_inputs[self._get_field_key_from_label("Random Seed (Optional):")]
                seed = int(seed) if seed is not None else None # Convert to int if provided

                # Additional check for non-negative standard deviations
                if terminal_value_growth_rate_std < 0 or discount_rate_std < 0 or exit_multiple_std < 0:
                    raise ValueError("Standard deviations cannot be negative.")

                # Ensure exit_year is consistent with base_free_cash_flows length
                if exit_year <= len(base_free_cash_flows):
                    raise ValueError(f"Exit Year ({exit_year}) must be greater than the number of provided base Free Cash Flows ({len(base_free_cash_flows)}).")

                results = simulate_private_equity_valuation_monte_carlo(
                    base_free_cash_flows=base_free_cash_flows,
                    terminal_value_growth_rate_mean=terminal_value_growth_rate_mean,
                    terminal_value_growth_rate_std=terminal_value_growth_rate_std,
                    discount_rate_mean=discount_rate_mean,
                    discount_rate_std=discount_rate_std,
                    exit_multiple_mean=exit_multiple_mean,
                    exit_multiple_std=exit_multiple_std,
                    num_simulations=num_simulations,
                    exit_year=exit_year,
                    seed=seed
                )
                output_message = (
                    f"Mean Valuation: {self.format_currency_output(results['mean_valuation'])}\n"
                    f"Median Valuation: {self.format_currency_output(results['median_valuation'])}\n"
                    f"5th Percentile Valuation: {self.format_currency_output(results['valuation_percentiles']['5th'])}\n"
                    f"25th Percentile Valuation: {self.format_currency_output(results['valuation_percentiles']['25th'])}\n"
                    f"75th Percentile Valuation: {self.format_currency_output(results['valuation_percentiles']['75th'])}\n"
                    f"95th Percentile Valuation: {self.format_currency_output(results['valuation_percentiles']['95th'])}"
                )
                self.display_result(output_message)

        except ValueError as e:
            logger.warning(f"Calculation error for {selected_model}: {e}")
            self.display_result(f"Input Error: {e}", is_error=True)
        except RuntimeError as e: # Specifically for Merton Model convergence or other runtime issues
            logger.error(f"Runtime error during calculation for {selected_model}: {e}")
            self.display_result(f"Calculation Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Calculation error (division by zero) for {selected_model}: {e}")
            self.display_result(f"Calculation Error: Division by zero. Check inputs.", is_error=True)
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

# Example usage (for testing PrivateMarketsAndCreditRiskGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Private Markets & Credit Risk Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x750") # Adjust size as needed

    # style = ttk.Style()
    # style.theme_use('clam')

    # For isolation testing, a simple frame acts as the parent
    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    private_markets_gui = PrivateMarketsAndCreditRiskGUI(test_parent_frame, controller=None)
    private_markets_gui.pack(fill="both", expand=True)

    root.mainloop()