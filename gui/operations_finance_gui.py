#gui/operations_finance_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, List, Any, Tuple
import re # Used for field key generation consistency

# Import BaseGUI for inheritance
from .base_gui import BaseGUI

# Import all functions from operations_finance_models
try:
    from mathematical_functions.operations_finance_models import (
        calculate_eoq,
        calculate_reorder_point,
        calculate_newsvendor_optimal_quantity,
        calculate_cascaded_pricing_protection_levels
    )
except ImportError:
    logging.error("Could not import operations_finance_models.py. Ensure it's in mathematical_functions and correct.")
    # Define dummy functions for graceful degradation during development/testing
    def calculate_eoq(*args, **kwargs):
        logging.warning("Dummy calculate_eoq called.")
        return {"error": "Mathematical function not found."}
    def calculate_reorder_point(*args, **kwargs):
        logging.warning("Dummy calculate_reorder_point called.")
        return {"error": "Mathematical function not found."}
    def calculate_newsvendor_optimal_quantity(*args, **kwargs):
        logging.warning("Dummy calculate_newsvendor_optimal_quantity called.")
        return {"error": "Mathematical function not found."}
    def calculate_cascaded_pricing_protection_levels(*args, **kwargs):
        logging.warning("Dummy calculate_cascaded_pricing_protection_levels called.")
        return {"error": "Mathematical function not found."}

# Import validation functions from utils
from utils.validation import validate_newsvendor_demand_params, validate_fare_classes

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class OperationsFinanceGUI(BaseGUI):
    """
    GUI module for various Operations Finance models, including EOQ, ROP,
    Newsvendor, and Cascaded Pricing.
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)

        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Operations Finance Models", font=("Arial", 16, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        self.selected_model_var = tk.StringVar(value="Select a Model")
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {} # To hold all model-specific frames

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        self._create_all_model_input_widgets(start_row=2)

        self._hide_all_input_frames() # Hide all initially

        self.calculate_button.config(text="Calculate", command=self.calculate_selected_model)
        logger.info("OperationsFinanceGUI initialized.")

        # Specific members for Cascaded Pricing dynamic inputs
        self.fare_class_entries: List[Dict[str, Any]] = [] # Stores Tkinter vars and frames for dynamic fare classes
        self.fare_class_frames: List[ttk.LabelFrame] = [] # Stores just the frames for easier destruction

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        """Creates the dropdown for selecting the specific Operations Finance model."""
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Operations Finance Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "Economic Order Quantity (EOQ)",
            "Reorder Point (ROP)",
            "Newsvendor Model",
            "Cascaded Pricing (Revenue Management)"
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
        """Creates all input fields and frames for each model, keeps them hidden."""
        parent_for_models = self.scrollable_frame

        # EOQ Inputs
        self.model_input_frames["Economic Order Quantity (EOQ)"] = self._create_eoq_widgets(parent_for_models)
        self.model_input_frames["Economic Order Quantity (EOQ)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # ROP Inputs
        self.model_input_frames["Reorder Point (ROP)"] = self._create_rop_widgets(parent_for_models)
        self.model_input_frames["Reorder Point (ROP)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Newsvendor Inputs
        self.model_input_frames["Newsvendor Model"] = self._create_newsvendor_widgets(parent_for_models)
        self.model_input_frames["Newsvendor Model"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Cascaded Pricing Inputs
        self.model_input_frames["Cascaded Pricing (Revenue Management)"] = self._create_cascaded_pricing_widgets(parent_for_models)
        self.model_input_frames["Cascaded Pricing (Revenue Management)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")


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
        logger.info(f"Selected Operations Finance model: {selected_model}")
        self._hide_all_input_frames()
        if selected_model in self.model_input_frames:
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
            # If Cascaded Pricing, ensure at least two fare classes are present (or desired minimum)
            if selected_model == "Cascaded Pricing (Revenue Management)":
                if not self.fare_class_entries: # Only add if none exist
                    self.add_fare_class_inputs()
                    self.add_fare_class_inputs()
                self._update_cascaded_pricing_fare_class_numbers() # Re-label if needed
        else:
            self.display_result("Please select a valid model.", is_error=True)
            logger.error(f"Invalid model selected: {selected_model}")

    def _get_field_key_from_label(self, label_text: str) -> str:
        """
        Generates a consistent key from a label text, handling suffixes for dynamic fields.
        """
        match = re.match(r"(.*)(_fc\d+)$", label_text)
        if match:
            base_label = match.group(1)
            suffix_part = match.group(2)
        else:
            base_label = label_text
            suffix_part = ""

        field_key = base_label.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip()
        field_key = field_key.replace(' ', '_') + suffix_part
        return field_key

    # --- EOQ Widgets and Calculation ---
    def _create_eoq_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates the input fields for the EOQ model."""
        frame = ttk.LabelFrame(parent_frame, text="Economic Order Quantity (EOQ) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        self.create_input_row(frame, row_idx, "Annual Demand (D):", "10000", "Total demand for the item over a year.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Ordering Cost per Order (S):", "50.00", "Cost incurred each time an order is placed.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Holding Cost per Unit per Year (H):", "2.00", "Cost of holding one unit in inventory for one year.")
        row_idx += 1
        return frame

    def _calculate_eoq_model(self):
        """Calculates EOQ and displays results."""
        fields = {
            "annual_demand_d": {"label": "Annual Demand (D):", "type": "positive_numeric"},
            "ordering_cost_per_order_s": {"label": "Ordering Cost per Order (S):", "type": "positive_numeric"},
            "holding_cost_per_unit_per_year_h": {"label": "Holding Cost per Unit per Year (H):", "type": "positive_numeric"},
        }
        validated_inputs = {}
        all_valid = True
        for key, info in fields.items():
            value_str = self.get_input_value(key)
            is_valid, processed_value = self.validate_input(value_str, info["type"], info["label"].replace(":", ""))
            if not is_valid:
                self.display_result(processed_value, is_error=True)
                all_valid = False
                break
            validated_inputs[key] = processed_value
        if not all_valid:
            return

        D = validated_inputs["annual_demand_d"]
        S = validated_inputs["ordering_cost_per_order_s"]
        H = validated_inputs["holding_cost_per_unit_per_year_h"]

        result = calculate_eoq(annual_demand=D, ordering_cost_per_order=S, holding_cost_per_unit_per_year=H)

        if "error" in result:
            self.display_result(result["error"], is_error=True)
        else:
            result_text = (
                f"Optimal Order Quantity (EOQ): {self.format_number_output(result['eoq'], 0)} units\n"
                f"Total Annual Cost: {self.format_currency_output(result['total_annual_cost'])}"
            )
            self.display_result(result_text)

    # --- ROP Widgets and Calculation ---
    def _create_rop_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates the input fields for the ROP model."""
        frame = ttk.LabelFrame(parent_frame, text="Reorder Point (ROP) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        self.create_input_row(frame, row_idx, "Average Daily Demand:", "100", "Average number of units demanded per day.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Lead Time (Days):", "7", "Number of days between placing an order and receiving it.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Desired Service Level (%):", "95", "Probability of not stocking out during lead time (e.g., 95 for 95%).")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Std Dev of Daily Demand:", "10", "Variability of daily demand. Enter 0 for no variability (no safety stock).")
        row_idx += 1
        return frame

    def _calculate_rop_model(self):
        """Calculates ROP and displays results."""
        fields = {
            "average_daily_demand": {"label": "Average Daily Demand:", "type": "non_negative_numeric"},
            "lead_time_days": {"label": "Lead Time (Days):", "type": "non_negative_numeric"},
            "desired_service_level": {"label": "Desired Service Level (%):", "type": "numeric_range_0_100"},
            "std_dev_of_daily_demand": {"label": "Std Dev of Daily Demand:", "type": "non_negative_numeric"},
        }
        validated_inputs = {}
        all_valid = True
        for key, info in fields.items():
            value_str = self.get_input_value(key)
            is_valid, processed_value = self.validate_input(value_str, info["type"], info["label"].replace(":", ""))
            if not is_valid:
                self.display_result(processed_value, is_error=True)
                all_valid = False
                break
            validated_inputs[key] = processed_value
        if not all_valid:
            return

        daily_demand = validated_inputs["average_daily_demand"]
        lead_time_days = validated_inputs["lead_time_days"]
        service_level_percent = validated_inputs["desired_service_level"]
        std_dev_daily_demand = validated_inputs["std_dev_of_daily_demand"]

        # Convert service level percentage to a fraction (0 to 1) for the model
        service_level = service_level_percent / 100.0

        result = calculate_reorder_point(
            daily_demand=daily_demand,
            lead_time_days=lead_time_days,
            service_level=service_level,
            std_dev_daily_demand=std_dev_daily_demand
        )

        if "error" in result:
            self.display_result(result["error"], is_error=True)
        else:
            result_text = (
                f"Reorder Point (ROP): {self.format_number_output(result['reorder_point'], 0)} units\n"
                f"Calculated Safety Stock: {self.format_number_output(result['safety_stock'], 0)} units"
            )
            self.display_result(result_text)

# --- Newsvendor Widgets and Calculation ---
    def _create_newsvendor_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """
        Creates the input fields for the Newsvendor model, including cost inputs
        and a dynamic section for demand distribution parameters (Normal or Uniform).
        """
        frame = ttk.LabelFrame(parent_frame, text="Newsvendor Model Inputs")
        frame.grid_columnconfigure(1, weight=1)

        # Core Costs
        row_idx = 0
        self.create_input_row(frame, row_idx, "Cost of Understocking (Cu):", "5.00", "Profit lost for each unit of unmet demand.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "Cost of Overstocking (Co):", "2.00", "Cost incurred for each unit of unsold inventory.")
        row_idx += 1

        # Demand Type Selection
        demand_type_frame = ttk.LabelFrame(frame, text="Demand Distribution Type")
        demand_type_frame.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        demand_type_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1 # Increment row_idx for the next set of widgets (demand parameters)

        ttk.Label(demand_type_frame, text="Select Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.newsvendor_demand_type_var = tk.StringVar(value="Normal Distribution")
        newsvendor_demand_options = ["Normal Distribution", "Uniform Distribution"]
        self.newsvendor_demand_combobox = ttk.Combobox(
            demand_type_frame,
            textvariable=self.newsvendor_demand_type_var,
            values=newsvendor_demand_options,
            state="readonly"
        )
        self.newsvendor_demand_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # Bind the selection event to the handler
        self.newsvendor_demand_combobox.bind("<<ComboboxSelected>>", self._on_newsvendor_demand_type_selected)

        # Demand Parameters Containers (hidden initially)
        self.newsvendor_demand_frames: Dict[str, ttk.LabelFrame] = {}
        self.newsvendor_demand_field_keys: Dict[str, List[str]] = {} # To keep track of keys for dynamic validation

        # Create and grid both demand type frames, then immediately hide them.
        # Store their intended grid row for later display.
        self.newsvendor_demand_frames["Normal Distribution"] = self._create_normal_demand_widgets_newsvendor(frame)
        self.newsvendor_demand_frames["Normal Distribution"].grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.newsvendor_normal_frame_row = row_idx # Store the row for Normal
        # DO NOT increment row_idx here, as both normal and uniform frames
        # will share this same grid row in their parent, but only one will be visible at a time.

        self.newsvendor_demand_frames["Uniform Distribution"] = self._create_uniform_demand_widgets_newsvendor(frame)
        self.newsvendor_demand_frames["Uniform Distribution"].grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.newsvendor_uniform_frame_row = row_idx # Store the row for Uniform
        # This row_idx (which is `row_idx` from before incrementing after demand_type_frame)
        # is the fixed row where demand parameter frames will appear.
        self.newsvendor_demand_params_display_row = row_idx

        self._hide_all_newsvendor_demand_frames() # Hide all initially

        # Show the default selected one (Normal Distribution) using its stored row
        self._on_newsvendor_demand_type_selected(initial_call=True)

        return frame

    def _hide_all_newsvendor_demand_frames(self):
        """Hides all Newsvendor demand-specific input frames."""
        for frame in self.newsvendor_demand_frames.values():
            frame.grid_forget()

    def _on_newsvendor_demand_type_selected(self, event=None, initial_call=False):
        """
        Callback when a Newsvendor demand type is selected from the combobox.
        Hides all demand parameter frames and displays the selected one at a fixed row.
        """
        selected_type = self.newsvendor_demand_type_var.get()
        self._hide_all_newsvendor_demand_frames()

        # The demand parameter frames (Normal/Uniform) always occupy the same grid row
        # within the overall Newsvendor Model Inputs frame.
        # This prevents the KeyError as we don't rely on grid_info() of an ungridded widget.
        display_row = self.newsvendor_demand_params_display_row

        if selected_type in self.newsvendor_demand_frames:
            self.newsvendor_demand_frames[selected_type].grid(
                row=display_row, # Use the pre-determined fixed row
                column=0, columnspan=2, padx=5, pady=5, sticky="nsew"
            )
            if not initial_call: # Only log if it's a user interaction, not initial setup
                logger.info(f"Newsvendor demand type set to: {selected_type}")
        else:
            logger.error(f"Invalid Newsvendor demand type selected: {selected_type}")

    def _create_normal_demand_widgets_newsvendor(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for Normal Distribution demand for Newsvendor."""
        frame = ttk.LabelFrame(parent_frame, text="Normal Distribution Demand Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0
        self.create_input_row(frame, row_idx, "Mean Demand (μ)_newsvendor:", "1000", "Average demand expected.")
        field_keys.append(self._get_field_key_from_label("Mean Demand (μ)_newsvendor:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Standard Deviation of Demand (σ)_newsvendor:", "100", "Variability of demand.")
        field_keys.append(self._get_field_key_from_label("Standard Deviation of Demand (σ)_newsvendor:"))
        row_idx += 1

        self.newsvendor_demand_field_keys["Normal Distribution"] = field_keys
        return frame

    def _create_uniform_demand_widgets_newsvendor(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates widgets for Uniform Distribution demand for Newsvendor."""
        frame = ttk.LabelFrame(parent_frame, text="Uniform Distribution Demand Inputs")
        frame.grid_columnconfigure(1, weight=1)

        field_keys = []
        row_idx = 0
        self.create_input_row(frame, row_idx, "Min Demand_newsvendor:", "800", "Minimum possible demand.")
        field_keys.append(self._get_field_key_from_label("Min Demand_newsvendor:"))
        row_idx += 1

        self.create_input_row(frame, row_idx, "Max Demand_newsvendor:", "1200", "Maximum possible demand.")
        field_keys.append(self._get_field_key_from_label("Max Demand_newsvendor:"))
        row_idx += 1

        self.newsvendor_demand_field_keys["Uniform Distribution"] = field_keys
        return frame

    def _calculate_newsvendor_model(self):
        """Calculates Newsvendor optimal quantity and displays results."""
        cu_key = self._get_field_key_from_label("Cost of Understocking (Cu):")
        co_key = self._get_field_key_from_label("Cost of Overstocking (Co):")

        # Validate core costs first
        is_valid_cu, cu = self.validate_input(self.get_input_value(cu_key), 'positive_numeric', "Cost of Understocking (Cu)")
        is_valid_co, co = self.validate_input(self.get_input_value(co_key), 'positive_numeric', "Cost of Overstocking (Co)")

        if not is_valid_cu:
            self.display_result(cu, is_error=True)
            return
        if not is_valid_co:
            self.display_result(co, is_error=True)
            return

        selected_demand_type = self.newsvendor_demand_type_var.get()
        demand_params_raw = {}
        all_demand_valid = True

        if selected_demand_type == "Normal Distribution":
            mean_key = self._get_field_key_from_label("Mean Demand (μ)_newsvendor:")
            std_dev_key = self._get_field_key_from_label("Standard Deviation of Demand (σ)_newsvendor:")

            is_valid_mean, mean_val = self.validate_input(self.get_input_value(mean_key), 'non_negative_numeric', "Mean Demand")
            is_valid_std_dev, std_dev_val = self.validate_input(self.get_input_value(std_dev_key), 'non_negative_numeric', "Standard Deviation of Demand")

            if not is_valid_mean: all_demand_valid = False; self.display_result(mean_val, is_error=True); return
            if not is_valid_std_dev: all_demand_valid = False; self.display_result(std_dev_val, is_error=True); return

            demand_params_raw = {'mean': mean_val, 'std_dev': std_dev_val}
            demand_type_for_func = "normal"

        elif selected_demand_type == "Uniform Distribution":
            min_key = self._get_field_key_from_label("Min Demand_newsvendor:")
            max_key = self._get_field_key_from_label("Max Demand_newsvendor:")

            is_valid_min, min_val = self.validate_input(self.get_input_value(min_key), 'non_negative_numeric', "Min Demand")
            is_valid_max, max_val = self.validate_input(self.get_input_value(max_key), 'non_negative_numeric', "Max Demand")

            if not is_valid_min: all_demand_valid = False; self.display_result(min_val, is_error=True); return
            if not is_valid_max: all_demand_valid = False; self.display_result(max_val, is_error=True); return

            demand_params_raw = {'min': min_val, 'max': max_val}
            demand_type_for_func = "uniform"
        else:
            self.display_result("Please select a valid demand type for Newsvendor.", is_error=True)
            return

        # Validate demand parameters using the model's internal validation function
        is_demand_params_valid, demand_params_processed = validate_newsvendor_demand_params(demand_type_for_func, demand_params_raw)
        if not is_demand_params_valid:
            self.display_result(demand_params_processed, is_error=True) # `demand_params_processed` holds the error message here
            return

        result = calculate_newsvendor_optimal_quantity(
            cost_understock=cu,
            cost_overstock=co,
            demand_type=demand_type_for_func,
            demand_params=demand_params_processed
        )

        if "error" in result:
            self.display_result(result["error"], is_error=True)
        else:
            result_text = (
                f"Critical Ratio: {self.format_percentage_output(result['critical_ratio'])}\n"
                f"Optimal Order Quantity: {self.format_number_output(result['optimal_quantity'], 0)} units\n"
            )
            # Only show expected leftover/stockout if they are non-None
            if result.get('expected_leftover') is not None:
                result_text += f"Expected Leftover: {self.format_number_output(result['expected_leftover'], 0)} units\n"
            if result.get('expected_stockout') is not None:
                result_text += f"Expected Stockout: {self.format_number_output(result['expected_stockout'], 0)} units"

            self.display_result(result_text)

    # --- Cascaded Pricing Widgets and Calculation ---
    def _create_cascaded_pricing_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        """Creates the input fields for the Cascaded Pricing model."""
        frame = ttk.LabelFrame(parent_frame, text="Cascaded Pricing Inputs")
        frame.grid_columnconfigure(1, weight=1)

        # Core Inputs
        row_idx = 0
        self.create_input_row(frame, row_idx, "Total Capacity:", "100", "Overall capacity available (e.g., seats on a flight).")
        row_idx += 1

        # Buttons for dynamic fare class management
        management_frame = ttk.Frame(frame)
        management_frame.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        management_frame.grid_columnconfigure(0, weight=1)
        management_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ttk.Button(management_frame, text="Add Fare Class", command=self.add_fare_class_inputs).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(management_frame, text="Remove Last Fare Class", command=self.remove_last_fare_class_inputs).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Container for dynamically added fare class inputs
        self.fare_classes_container = ttk.LabelFrame(frame, text="Fare Classes (Higher Price to Lower Price)")
        self.fare_classes_container.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.fare_classes_container.grid_columnconfigure(1, weight=1)
        # No row_idx increment here as its content is managed by pack, not grid, relative to this frame.
        return frame

    def add_fare_class_inputs(self):
        """Dynamically adds a new set of input fields for a fare class."""
        fare_class_num = len(self.fare_class_entries) + 1
        frame_text = f"Fare Class {fare_class_num}"
        fare_class_frame = ttk.LabelFrame(self.fare_classes_container, text=frame_text)
        fare_class_frame.pack(fill="x", padx=5, pady=5) # Pack within the fare_classes_container
        fare_class_frame.grid_columnconfigure(1, weight=1)

        # Use StringVar for dynamic entries
        price_var = tk.StringVar(value="100.00")
        demand_mean_var = tk.StringVar(value="50.00")
        demand_std_dev_var = tk.StringVar(value="10.00")

        # Create input rows. The key suffix is crucial for uniqueness and retrieval.
        row_idx = 0
        self.create_input_row(fare_class_frame, row_idx, f"Price_fc{fare_class_num}:", price_var, "Price of this fare class.")
        row_idx += 1
        self.create_input_row(fare_class_frame, row_idx, f"Demand Mean_fc{fare_class_num}:", demand_mean_var, "Average demand for this class.")
        row_idx += 1
        self.create_input_row(fare_class_frame, row_idx, f"Demand Std Dev_fc{fare_class_num}:", demand_std_dev_var, "Standard deviation of demand for this class.")
        row_idx += 1

        self.fare_class_entries.append({
            'price_var': price_var,
            'demand_mean_var': demand_mean_var,
            'demand_std_dev_var': demand_std_dev_var,
            'frame': fare_class_frame
        })
        self.fare_class_frames.append(fare_class_frame)
        logger.info(f"Added Fare Class {fare_class_num}.")

    def remove_last_fare_class_inputs(self):
        """Removes the last added set of input fields for a fare class."""
        if len(self.fare_class_entries) > 1: # Always keep at least one fare class
            last_fc_dict = self.fare_class_entries.pop()
            last_frame = self.fare_class_frames.pop()
            last_frame.destroy()

            # Remove corresponding entries from self.input_fields
            # The keys are tied to the fare class number, so we need to know WHICH one was removed.
            # This is implicitly the highest numbered one if always removing the last.
            fare_class_num = len(self.fare_class_entries) + 1 # This is the number of the one just removed
            keys_to_remove = [
                self._get_field_key_from_label(f"Price_fc{fare_class_num}:"),
                self._get_field_key_from_label(f"Demand Mean_fc{fare_class_num}:"),
                self._get_field_key_from_label(f"Demand Std Dev_fc{fare_class_num}:"),
            ]
            for key in keys_to_remove:
                if key in self.input_fields:
                    del self.input_fields[key]
                else:
                    logger.warning(f"Attempted to delete non-existent input field key: {key}")

            # Re-label remaining fare classes if necessary (optional, but good for UI)
            self._update_cascaded_pricing_fare_class_numbers()
            logger.info(f"Removed Fare Class {fare_class_num}.")
        elif len(self.fare_class_entries) == 1:
            messagebox.showinfo("Cascaded Pricing", "You must have at least one fare class.")
        else:
            messagebox.showinfo("Cascaded Pricing", "No fare classes to remove.")

    def _update_cascaded_pricing_fare_class_numbers(self):
        """Updates the label frame titles and input keys if fare classes are removed from the middle or reordered."""
        # This function is primarily useful if you allow removal from anywhere,
        # or want to re-number after a "clear all" then "add".
        # For simple "remove last", it's less critical but harmless.
        for i, fc_dict in enumerate(self.fare_class_entries):
            old_frame_text = fc_dict['frame'].cget("text")
            new_frame_text = f"Fare Class {i+1}"
            if old_frame_text != new_frame_text:
                fc_dict['frame'].config(text=new_frame_text)
                # If we were strictly re-indexing internal self.input_fields keys,
                # this would be the place to update them.
                # Currently, our system generates keys like `price_fc1` and `price_fc2`,
                # and when one is removed, the remaining ones keep their old numbers.
                # For simplicity and correctness with our current key mapping,
                # we are relying on the actual *key* in self.input_fields remaining unchanged
                # if the entry itself isn't destroyed.
                # Since we always destroy the last one, this re-labeling is purely cosmetic
                # in this specific implementation, but good practice.
                # If we ever allowed arbitrary removal (not just last),
                # a more complex re-keying logic would be needed here.


    def _calculate_cascaded_pricing_model(self):
        """Calculates Cascaded Pricing protection levels and displays results."""
        capacity_key = self._get_field_key_from_label("Total Capacity:")
        is_valid_capacity, capacity = self.validate_input(self.get_input_value(capacity_key), 'positive_numeric', "Total Capacity")

        if not is_valid_capacity:
            self.display_result(capacity, is_error=True)
            return

        fare_classes_data_for_model = []
        all_fare_classes_valid = True

        if not self.fare_class_entries:
            self.display_result("Please add at least one fare class.", is_error=True)
            return

        # Gather data from dynamic fare class inputs
        for i, fc_dict in enumerate(self.fare_class_entries):
            fc_num = i + 1 # For identification in error messages
            price_key = self._get_field_key_from_label(f"Price_fc{fc_num}:")
            demand_mean_key = self._get_field_key_from_label(f"Demand Mean_fc{fc_num}:")
            demand_std_dev_key = self._get_field_key_from_label(f"Demand Std Dev_fc{fc_num}:")

            price_str = self.get_input_value(price_key)
            demand_mean_str = self.get_input_value(demand_mean_key)
            demand_std_dev_str = self.get_input_value(demand_std_dev_key)

            # Validate individual fields within the fare class
            is_valid_price, price = self.validate_input(price_str, 'positive_numeric', f"Fare Class {fc_num} Price")
            is_valid_mean, demand_mean = self.validate_input(demand_mean_str, 'non_negative_numeric', f"Fare Class {fc_num} Demand Mean")
            is_valid_std_dev, demand_std_dev = self.validate_input(demand_std_dev_str, 'non_negative_numeric', f"Fare Class {fc_num} Demand Std Dev")

            if not all([is_valid_price, is_valid_mean, is_valid_std_dev]):
                all_fare_classes_valid = False
                if not is_valid_price: self.display_result(price, is_error=True)
                elif not is_valid_mean: self.display_result(demand_mean, is_error=True)
                elif not is_valid_std_dev: self.display_result(demand_std_dev, is_error=True)
                return # Stop at first error

            fare_classes_data_for_model.append({
                'price': price,
                'demand_mean': demand_mean,
                'demand_std_dev': demand_std_dev,
                'name': f"Fare Class {fc_num}" # Optional name for debugging in model
            })

        if not all_fare_classes_valid:
            return # Already displayed error above

        # Now, pass the gathered and individually validated data to the centralized validator
        is_fare_classes_structurally_valid, validation_message_or_data = validate_fare_classes(fare_classes_data_for_model)

        if not is_fare_classes_structurally_valid:
            self.display_result(validation_message_or_data, is_error=True)
            return

        # Proceed with calculation using the validated and potentially reordered/cleaned data from validator
        # Note: validate_fare_classes returns the *original* list if valid, so we use that.
        result = calculate_cascaded_pricing_protection_levels(
            total_capacity=capacity,
            fare_classes=validation_message_or_data # This now contains the fully validated list
        )

        if "error" in result:
            self.display_result(result["error"], is_error=True)
        else:
            protection_levels = result['protection_levels']
            result_text = "Optimal Protection Levels (Booking Limits):\n"
            # It's important to present results back in the user's input order for clarity
            # The `protection_levels` result from the function is already re-ordered to match original input indices.
            for i, level in enumerate(protection_levels):
                # We need to retrieve the original price for display, assuming fare_classes_data_for_model is still in order
                original_price = fare_classes_data_for_model[i]['price']
                result_text += (
                    f"  Fare Class {i+1} (Price: {self.format_currency_output(original_price)}): "
                    f"{self.format_number_output(level, 0)} units\n"
                )
            # Add total available capacity for context
            result_text += f"\nTotal Capacity: {self.format_number_output(capacity, 0)} units"
            self.display_result(result_text)

    # --- Main Calculation Dispatcher ---
    def calculate_selected_model(self):
        """Dispatches to the appropriate calculation method based on selected model."""
        self.display_result("Calculating...", is_error=False)
        self.display_result("")

        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Model":
            self.display_result("Please select an Operations Finance model to calculate.", is_error=True)
            return

        try:
            if selected_model == "Economic Order Quantity (EOQ)":
                self._calculate_eoq_model()
            elif selected_model == "Reorder Point (ROP)":
                self._calculate_rop_model()
            elif selected_model == "Newsvendor Model":
                self._calculate_newsvendor_model()
            elif selected_model == "Cascaded Pricing (Revenue Management)":
                self._calculate_cascaded_pricing_model()
            else:
                self.display_result("Unknown model selected. Please select from the list.", is_error=True)
                logger.error(f"Unknown model selected in dispatcher: {selected_model}")
        except Exception as e:
            logger.critical(f"An unexpected error occurred during calculation dispatch for {selected_model}: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        """
        Overrides BaseGUI's clear_inputs to also reset the model selection
        and update the UI state.
        """
        super().clear_inputs()
        self.selected_model_var.set("Select a Model")
        self.newsvendor_demand_type_var.set("Normal Distribution") # Reset newsvendor default
        self._on_model_selected() # Trigger main model UI update to hide frames and clear messages

        # Clear and reset Cascaded Pricing dynamic fare classes
        for frame in self.fare_class_frames:
            frame.destroy()
        self.fare_class_frames.clear()
        self.fare_class_entries.clear()
        # No need to add defaults here, _on_model_selected handles it when Cascaded is picked again.


# Example usage (for testing OperationsFinanceGUI in isolation)
if __name__ == "__main__":
    import sys
    import os

    # Add the parent directory of financial_calculator to sys.path
    # This allows imports like 'financial_calculator.gui.base_gui' to work.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    sys.path.insert(0, project_root)

    # Ensure config and utils are importable for standalone execution
    # This might require some careful path management depending on how your project root is structured
    try:
        from config import DEFAULT_WINDOW_WIDTH
        # Also need a dummy BaseGUI and utils.validation if running without full project
        # For simplicity, assuming BaseGUI and utils.validation are correctly found by the sys.path modification
        from financial_calculator.gui.base_gui import BaseGUI
        from financial_calculator.utils.validation import validate_input_factory, ValidationFunctions
    except ImportError as e:
        print(f"Error importing necessary modules: {e}")
        print("Please ensure your Python path is correctly set up to run this script independently.")
        print("For standalone testing, you might need dummy implementations for missing imports.")
        sys.exit(1)


    root = tk.Tk()
    root.title("Operations Finance Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x700")

    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    # Instantiate the GUI
    operations_finance_gui = OperationsFinanceGUI(test_parent_frame, controller=None)
    operations_finance_gui.pack(fill="both", expand=True)

    root.mainloop()