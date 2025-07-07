# financial_calculator/gui/yield_curve_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import Dict, Any, List, Union
import re
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .base_gui import BaseGUI
import mathematical_functions.yield_curve_models as models
from config import DEFAULT_WINDOW_WIDTH, DEFAULT_DECIMAL_PLACES_PERCENTAGE, DEFAULT_DECIMAL_PLACES_GENERAL

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class YieldCurveGUI(BaseGUI):
    """
    GUI module for various Yield Curve models (Nelson-Siegel, Svensson, Cubic Spline).
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Yield Curve Modeling", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        self.selected_model_var = tk.StringVar(value="Select a Model")

        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}
        self.model_input_widgets_map: Dict[str, Dict[str, Union[tk.Entry, scrolledtext.ScrolledText]]] = {}

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        
        model_input_start_row = 2
        self._create_all_model_input_widgets(start_row=model_input_start_row)

        self._hide_all_input_frames()

        # --- Plotting Area Setup (Crucial Change Here) ---
        self.plot_container_frame = ttk.LabelFrame(self.scrollable_frame, text="Yield Curve Plot", padding="10")
        self.plot_container_frame.grid(row=model_input_start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_rowconfigure(model_input_start_row + 1, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(7, 5))

        # IMPORTANT CHANGE: Use a different attribute name for the Matplotlib canvas
        self.matplotlib_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container_frame)
        self.matplotlib_canvas_widget = self.matplotlib_canvas.get_tk_widget()
        self.matplotlib_canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # IMPORTANT CHANGE: Link toolbar to the new Matplotlib canvas
        self.toolbar = NavigationToolbar2Tk(self.matplotlib_canvas, self.plot_container_frame)
        self.toolbar.update()
        self.matplotlib_canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ax.set_title('Yield Curve Plot')
        self.ax.set_xlabel('Maturity (Years)')
        self.ax.set_ylabel('Yield (%)')
        self.ax.grid(True)
        # IMPORTANT CHANGE: Draw on the new Matplotlib canvas
        self.matplotlib_canvas.draw()
        # --- End Plotting Area Setup ---


        self.calculate_button.config(text="Fit Yield Curve", command=self.calculate_selected_model)
        
        self.result_frame.grid(row=model_input_start_row + 2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=model_input_start_row + 3, column=0, columnspan=2, pady=5)


        logger.info("YieldCurveGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Yield Curve Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Nelson-Siegel Model",
            "Svensson Model",
            "Cubic Spline Model"
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
        parent_for_models = self.scrollable_frame

        self.model_input_frames["Nelson-Siegel Model"] = self._create_nelson_siegel_widgets(parent_for_models)
        self.model_input_frames["Nelson-Siegel Model"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.model_input_frames["Svensson Model"] = self._create_svensson_widgets(parent_for_models)
        self.model_input_frames["Svensson Model"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.model_input_frames["Cubic Spline Model"] = self._create_cubic_spline_widgets(parent_for_models)
        self.model_input_frames["Cubic Spline Model"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def _hide_all_input_frames(self):
        for frame in self.model_input_frames.values():
            frame.grid_forget()
        self.display_result("Select a yield curve model to view its inputs and fit the curve.", is_error=False)

    def _on_model_selected(self, event=None):
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected yield curve model: {selected_model}")
        self._hide_all_input_frames()
        if selected_model in self.model_input_frames:
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        else:
            self.display_result("Please select a valid model.", is_error=True)
            logger.warning(f"Attempted to select unknown model: {selected_model}")
        
        self.ax.clear()
        self.ax.set_title('Yield Curve Plot')
        self.ax.set_xlabel('Maturity (Years)')
        self.ax.set_ylabel('Yield (%)')
        self.ax.grid(True)
        # IMPORTANT CHANGE: Draw on the new Matplotlib canvas
        self.matplotlib_canvas.draw()


    # --- Widget creation methods for each model ---

    def _create_input_widget(self, parent_frame: ttk.LabelFrame, row_idx: int, label_text: str, default_value: str, tooltip_text: str, is_multiline: bool = False):
        ttk.Label(parent_frame, text=label_text).grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        
        field_key = self._get_field_key_from_label(label_text)
        
        if is_multiline:
            input_widget = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, width=40, height=5, font=("Arial", 9))
            input_widget.insert(tk.END, default_value)
        else:
            input_widget = ttk.Entry(parent_frame, width=40)
            input_widget.insert(0, default_value)
            
        input_widget.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        
        self.input_fields[field_key] = input_widget
        
        model_name = parent_frame.cget("text").replace(" Inputs", "")
        if model_name not in self.model_input_widgets_map:
            self.model_input_widgets_map[model_name] = {}
        self.model_input_widgets_map[model_name][field_key] = input_widget
        
        if hasattr(self, 'create_tooltip'):
            self.create_tooltip(input_widget, tooltip_text)
        else:
            logger.debug(f"Tooltip for {label_text} not created: create_tooltip method not found in BaseGUI or is not active.")


    def _create_nelson_siegel_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="Nelson-Siegel Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self._create_input_widget(frame, row_idx, "Maturities (Years, comma-separated):", "0.5,1,2,3,5,7,10,20,30", "Comma-separated list of bond maturities in years.", is_multiline=True)
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Observed Yields (%, comma-separated):", "1.5,1.8,2.2,2.5,2.8,3.0,3.2,3.5,3.6", "Comma-separated list of observed yields corresponding to maturities (e.g., 3.0 for 3%).", is_multiline=True)
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 0 (Initial, optional):", "0.03", "Initial guess for Beta 0 (long-term level factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 1 (Initial, optional):", "-0.02", "Initial guess for Beta 1 (short-term slope factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 2 (Initial, optional):", "-0.01", "Initial guess for Beta 2 (medium-term curvature factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Tau (Initial, optional):", "5.0", "Initial guess for Tau (decay factor), typically >0. Controls where curvature is maximized.")
        row_idx += 1

        return frame

    def _create_svensson_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="Svensson Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self._create_input_widget(frame, row_idx, "Maturities (Years, comma-separated):", "0.5,1,2,3,5,7,10,20,30", "Comma-separated list of bond maturities in years.", is_multiline=True)
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Observed Yields (%, comma-separated):", "1.5,1.8,2.2,2.5,2.8,3.0,3.2,3.5,3.6", "Comma-separated list of observed yields corresponding to maturities (e.g., 3.0 for 3%).", is_multiline=True)
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 0 (Initial, optional):", "0.03", "Initial guess for Beta 0 (long-term level factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 1 (Initial, optional):", "-0.02", "Initial guess for Beta 1 (short-term slope factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Beta 2 (Initial, optional):", "-0.01", "Initial guess for Beta 2 (first curvature factor).")
        row_idx += 1
            
        self._create_input_widget(frame, row_idx, "Beta 3 (Initial, optional):", "0.005", "Initial guess for Beta 3 (second curvature factor).")
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Tau 1 (Initial, optional):", "1.0", "Initial guess for Tau 1 (first decay factor), typically >0. Controls short-term curvature.")
        row_idx += 1
            
        self._create_input_widget(frame, row_idx, "Tau 2 (Initial, optional):", "5.0", "Initial guess for Tau 2 (second decay factor), typically >0 and different from Tau 1. Controls medium-term curvature.")
        row_idx += 1

        return frame

    def _create_cubic_spline_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="Cubic Spline Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self._create_input_widget(frame, row_idx, "Maturities (Years, comma-separated):", "0.5,1,2,3,5,7,10,20,30", "Comma-separated list of bond maturities in years.", is_multiline=True)
        row_idx += 1

        self._create_input_widget(frame, row_idx, "Observed Yields (%, comma-separated):", "1.5,1.8,2.2,2.5,2.8,3.0,3.2,3.5,3.6", "Comma-separated list of observed yields corresponding to maturities (e.g., 3.0 for 3%).", is_multiline=True)
        row_idx += 1

        return frame

    def _get_field_key_from_label(self, label_text: str) -> str:
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_')
        return field_key

    def _get_input_value_from_widget(self, model_name: str, label_text: str) -> str:
        field_key = self._get_field_key_from_label(label_text)
        widget = self.input_fields.get(field_key)
        
        if widget is None:
            logger.warning(f"Widget for model '{model_name}' and label '{label_text}' (key '{field_key}') not found in BaseGUI.input_fields.")
            return ""

        if isinstance(widget, scrolledtext.ScrolledText):
            return widget.get("1.0", tk.END).strip()
        elif isinstance(widget, ttk.Entry):
            return widget.get().strip()
        return ""


    def _parse_and_validate_list_input(self, model_name: str, label_text: str, field_name_for_error: str) -> np.ndarray:
        raw_string = self._get_input_value_from_widget(model_name, label_text)
        if not raw_string:
            raise ValueError(f"{field_name_for_error} cannot be empty.")
        
        is_valid, parsed_list = self.validate_input_list(raw_string, 'numeric', field_name_for_error)
        
        if not is_valid:
            raise ValueError(f"Input for {field_name_for_error} is invalid: {parsed_list}")
        
        return np.array(parsed_list)

    def _get_initial_param_value(self, model_name: str, label_text: str, default_value: float) -> float:
        value_str = self._get_input_value_from_widget(model_name, label_text)
        if not value_str:
            return default_value
        
        is_valid, parsed_value = self.validate_input(value_str, 'numeric', label_text)
        
        if not is_valid:
            raise ValueError(f"Invalid number format for '{label_text}': {parsed_value}")
        
        return float(parsed_value)


    # --- Calculation Logic ---

    def calculate_selected_model(self):
        self.display_result("Fitting yield curve...", is_error=False)
        self.ax.clear()
        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Model":
            self.display_result("Please select a yield curve model to fit.", is_error=True)
            return

        try:
            maturities = self._parse_and_validate_list_input(selected_model, "Maturities (Years, comma-separated):", "Maturities")
            observed_yields_percent = self._parse_and_validate_list_input(selected_model, "Observed Yields (%, comma-separated):", "Observed Yields")
            
            observed_yields = observed_yields_percent / 100.0

            if len(maturities) != len(observed_yields):
                raise ValueError("Error: Number of maturities must match the number of observed yields.")
            
            if np.any(maturities <= 0):
                raise ValueError("Error: All maturities must be positive numbers.")
            
            if np.any(observed_yields < -0.01):
                logger.warning("Observed yields contain significantly negative values, which might indicate unusual market conditions or input error.")

            sort_indices = np.argsort(maturities)
            maturities = maturities[sort_indices]
            observed_yields = observed_yields[sort_indices]

            fitted_params_dict = {}
            curve_yields_for_plot = None
            optim_result = None
            rmse = None
            r_squared = None
            fitted_model_object = None

            if len(maturities) > 1:
                min_m = np.min(maturities)
                max_m = np.max(maturities)
                extended_range = max(0.1, (max_m - min_m) * 0.2)
                maturities_to_plot = np.linspace(min_m, max_m + extended_range, 200)
            else:
                maturities_to_plot = np.linspace(maturities[0] * 0.5, maturities[0] * 1.5, 50) if maturities[0] > 0 else np.linspace(0.1, 1.0, 50)
                maturities_to_plot = np.maximum(maturities_to_plot, 1e-6)


            if selected_model == "Nelson-Siegel Model":
                if len(maturities) < 4:
                    raise ValueError("Nelson-Siegel model requires at least 4 data points.")
                initial_params = [
                    self._get_initial_param_value(selected_model, "Beta 0 (Initial, optional):", 0.03),
                    self._get_initial_param_value(selected_model, "Beta 1 (Initial, optional):", -0.02),
                    self._get_initial_param_value(selected_model, "Beta 2 (Initial, optional):", -0.01),
                    self._get_initial_param_value(selected_model, "Tau (Initial, optional):", 5.0)
                ]
                if initial_params[3] <= 0:
                    raise ValueError("Initial Tau for Nelson-Siegel must be positive.")

                result_dict = models.fit_nelson_siegel_curve(maturities, observed_yields, initial_params=initial_params)
                fitted_params_dict = {k: v for k, v in result_dict.items() if k not in ['optim_result', 'rmse', 'r_squared']}
                optim_result = result_dict.get('optim_result')
                rmse = result_dict.get('rmse')
                r_squared = result_dict.get('r_squared')
                
                curve_yields_for_plot = models.get_nelson_siegel_spot_yield_curve(maturities_to_plot, fitted_params_dict)
                
            elif selected_model == "Svensson Model":
                if len(maturities) < 6:
                    raise ValueError("Svensson model requires at least 6 data points.")
                initial_params = [
                    self._get_initial_param_value(selected_model, "Beta 0 (Initial, optional):", 0.03),
                    self._get_initial_param_value(selected_model, "Beta 1 (Initial, optional):", -0.02),
                    self._get_initial_param_value(selected_model, "Beta 2 (Initial, optional):", -0.01),
                    self._get_initial_param_value(selected_model, "Beta 3 (Initial, optional):", 0.005),
                    self._get_initial_param_value(selected_model, "Tau 1 (Initial, optional):", 1.0),
                    self._get_initial_param_value(selected_model, "Tau 2 (Initial, optional):", 5.0)
                ]
                if initial_params[4] <= 0 or initial_params[5] <= 0:
                    raise ValueError("Initial Tau 1 and Tau 2 for Svensson must be positive.")

                result_dict = models.fit_svensson_curve(maturities, observed_yields, initial_params=initial_params)
                fitted_params_dict = {k: v for k, v in result_dict.items() if k not in ['optim_result', 'rmse', 'r_squared']}
                optim_result = result_dict.get('optim_result')
                rmse = result_dict.get('rmse')
                r_squared = result_dict.get('r_squared')

                curve_yields_for_plot = models.get_svensson_spot_yield_curve(maturities_to_plot, fitted_params_dict)

            elif selected_model == "Cubic Spline Model":
                if len(maturities) < 2:
                    raise ValueError("Cubic Spline model requires at least 2 data points.")
                
                fitted_model_object = models.fit_cubic_spline_curve(maturities, observed_yields, end_conditions='natural')
                fitted_params_dict = {"CubicSpline_Object": "Internal interpolation coefficients"}

                curve_yields_for_plot = models.get_cubic_spline_spot_yield_curve(maturities_to_plot, fitted_model_object)
                
            else:
                raise ValueError("Internal error: Unknown model selected.")

            output_message = []
            output_message.append(f"--- {selected_model} Fit Results ---")
            
            for param, value in fitted_params_dict.items():
                if isinstance(value, (float, np.float64)):
                    output_message.append(f"{param}: {self.format_number_output(value, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                else:
                    output_message.append(f"{param}: {value}")
            
            if rmse is not None:
                output_message.append(f"RMSE: {self.format_number_output(rmse, DEFAULT_DECIMAL_PLACES_GENERAL)}")
            if r_squared is not None:
                output_message.append(f"R-squared: {self.format_number_output(r_squared, DEFAULT_DECIMAL_PLACES_GENERAL)}")

            if optim_result is not None:
                output_message.append(f"\nOptimization Status: {optim_result.message}")
                output_message.append(f"Number of function evaluations: {optim_result.nfev}")

            self.ax.clear()
            self.ax.plot(maturities, observed_yields * 100, 'o', label='Observed Yields (%)')
            if curve_yields_for_plot is not None:
                self.ax.plot(maturities_to_plot, curve_yields_for_plot * 100, '-', label=f'{selected_model} Curve (%)')
            
            self.ax.set_title(f'{selected_model} Yield Curve')
            self.ax.set_xlabel('Maturity (Years)')
            self.ax.set_ylabel('Yield (%)')
            self.ax.grid(True)
            self.ax.legend()
            self.fig.tight_layout()
            # IMPORTANT CHANGE: Draw on the new Matplotlib canvas
            self.matplotlib_canvas.draw()


            output_message.append("\n--- Fitted Yields for Standard Maturities ---")
            standard_maturities = np.array([0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 30])
            
            if selected_model == "Nelson-Siegel Model":
                standard_fitted_yields = models.get_nelson_siegel_spot_yield_curve(standard_maturities, fitted_params_dict)
            elif selected_model == "Svensson Model":
                standard_fitted_yields = models.get_svensson_spot_yield_curve(standard_maturities, fitted_params_dict)
            elif selected_model == "Cubic Spline Model":
                standard_fitted_yields = models.get_cubic_spline_spot_yield_curve(standard_maturities, fitted_model_object)
            else:
                standard_fitted_yields = np.full_like(standard_maturities, np.nan)

            for i, m in enumerate(standard_maturities):
                fitted_yield_decimal = standard_fitted_yields[i]
                if np.isnan(fitted_yield_decimal):
                    output_message.append(f"Yield at {m} Year(s): N/A")
                else:
                    output_message.append(f"Yield at {m} Year(s): {self.format_percentage_output(fitted_yield_decimal * 100)}")

            self.display_result("\n".join(output_message), is_error=False)

        except ValueError as e:
            logger.warning(f"Input/Calculation Error for {selected_model}: {e}")
            self.display_result(f"Input Error: {e}", is_error=True)
        except RuntimeError as e:
            logger.error(f"Fitting runtime error for {selected_model}: {e}", exc_info=True)
            self.display_result(f"Calculation Failed: {e}", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during {selected_model} fitting: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        for model_name, widgets_map in self.model_input_widgets_map.items():
            for field_key, widget in widgets_map.items():
                if isinstance(widget, scrolledtext.ScrolledText):
                    widget.delete("1.0", tk.END)
                elif isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
        
        self.display_result("", is_error=False)
        self.selected_model_var.set("Select a Model")
        self._on_model_selected()

        logger.info("YieldCurveGUI inputs cleared and model selection reset.")


# Example usage (for testing YieldCurveGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Yield Curve Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x900")

    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    yield_curve_gui = YieldCurveGUI(test_parent_frame, controller=None)
    yield_curve_gui.pack(fill="both", expand=True)

    root.mainloop()