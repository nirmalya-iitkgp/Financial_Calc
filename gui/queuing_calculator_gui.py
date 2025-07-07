# financial_calculator/gui/queuing_calculator_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import Dict, Any, Union

# Import the mathematical functions
import mathematical_functions.queuing_mm1 as mm1_models
import mathematical_functions.queuing_mg1 as mg1_models
import mathematical_functions.queuing_mmc as mmc_models

from .base_gui import BaseGUI
from config import DEFAULT_WINDOW_WIDTH, DEFAULT_DECIMAL_PLACES_GENERAL

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class QueuingCalculatorGUI(BaseGUI):
    """
    GUI module for various Queuing models (M/M/1, M/G/1, M/M/c).
    Inherits from BaseGUI for common functionalities.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs) # Ensure BaseGUI's init is called

        self.gui_title_label = ttk.Label(self.scrollable_frame, text="Queuing Theory Calculator", font=("Arial", 14, "bold"))
        self.gui_title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        self.selected_model_var = tk.StringVar(value="Select a Model")

        # Dictionaries to store frames for each model type
        self.model_input_frames: Dict[str, ttk.LabelFrame] = {}

        self.mg1_dist_type_var = tk.StringVar(value="Exponential") # For M/G/1 service distribution type

        # Store explicit references for M/G/1 dynamically shown/hidden widgets
        self.mg1_es2_label = None
        self.mg1_es2_entry = None
        self.mg1_uniform_min_label = None
        self.mg1_uniform_min_entry = None
        self.mg1_uniform_max_label = None
        self.mg1_uniform_max_entry = None

        # Store the field keys for M/G/1 specific inputs to retrieve values
        # These keys are derived from the *actual* label text that BaseGUI processes
        self.mg1_es2_key = "e_s2_second_moment_of_service_time" # From "E[S²] (Second Moment of Service Time):"
        self.mg1_uniform_min_key = "uniform_min_value_a" # From "Uniform Min Value (a):"
        self.mg1_uniform_max_key = "uniform_max_value_b" # From "Uniform Max Value (b):"
        
        # Define the unique keys for each model's primary inputs
        self.mm1_lambda_key = "mm1_arrival_rate"
        self.mm1_mu_key = "mm1_service_rate"
        self.mm1_n_key = "mm1_number_of_customers_n_for_p_n"

        self.mg1_lambda_key = "mg1_arrival_rate"
        self.mg1_mu_key = "mg1_service_rate"

        self.mmc_lambda_key = "mmc_arrival_rate"
        self.mmc_mu_key = "mmc_service_rate_per_server"
        self.mmc_c_key = "mmc_number_of_servers_c"

        self._create_model_selection_widgets(self.scrollable_frame, start_row=1)
        
        model_input_start_row = 2
        self._create_all_model_input_widgets(start_row=model_input_start_row)

        self._hide_all_input_frames()

        self.calculate_button.config(text="Calculate Queuing Metrics", command=self.calculate_queuing_metrics)
        
        # Adjust grid rows for common elements based on where model inputs end
        self.result_frame.grid(row=model_input_start_row + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.common_buttons_frame.grid(row=model_input_start_row + 2, column=0, columnspan=2, pady=5)

        logger.info("QueuingCalculatorGUI initialized.")

    def _create_model_selection_widgets(self, parent_frame: ttk.Frame, start_row: int):
        model_select_frame = ttk.LabelFrame(parent_frame, text="Select Queuing Model")
        model_select_frame.grid(row=start_row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        model_select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_select_frame, text="Model Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.model_options = [
            "M/M/1 (Single Server, Exponential Service)",
            "M/G/1 (Single Server, General Service)",
            "M/M/c (Multiple Servers, Exponential Service)"
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

        # M/M/1 Model Inputs
        self.model_input_frames["M/M/1 (Single Server, Exponential Service)"] = self._create_mm1_widgets(parent_for_models)
        self.model_input_frames["M/M/1 (Single Server, Exponential Service)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # M/G/1 Model Inputs
        self.model_input_frames["M/G/1 (Single Server, General Service)"] = self._create_mg1_widgets(parent_for_models)
        self.model_input_frames["M/G/1 (Single Server, General Service)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # M/M/c Model Inputs
        self.model_input_frames["M/M/c (Multiple Servers, Exponential Service)"] = self._create_mmc_widgets(parent_for_models)
        self.model_input_frames["M/M/c (Multiple Servers, Exponential Service)"].grid(row=start_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def _hide_all_input_frames(self):
        for frame in self.model_input_frames.values():
            frame.grid_forget()
        self.display_result("Select a queuing model to view its inputs.", is_error=False)

    def _on_model_selected(self, event=None):
        selected_model = self.selected_model_var.get()
        logger.info(f"Selected queuing model: {selected_model}")
        self._hide_all_input_frames()

        # Hide M/G/1 specific labels/entries explicitly when switching away
        if self.mg1_es2_label: self.mg1_es2_label.grid_forget()
        if self.mg1_es2_entry: self.mg1_es2_entry.grid_forget()
        if self.mg1_uniform_min_label: self.mg1_uniform_min_label.grid_forget()
        if self.mg1_uniform_min_entry: self.mg1_uniform_min_entry.grid_forget()
        if self.mg1_uniform_max_label: self.mg1_uniform_max_label.grid_forget()
        if self.mg1_uniform_max_entry: self.mg1_uniform_max_entry.grid_forget()

        if selected_model in self.model_input_frames:
            self.model_input_frames[selected_model].grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
            if selected_model == "M/G/1 (Single Server, General Service)":
                # Trigger update for M/G/1 specific fields
                self._on_mg1_distribution_selected()
        else:
            self.display_result("Please select a valid model.", is_error=True)
            logger.warning(f"Attempted to select unknown model: {selected_model}")
        self.display_result("", is_error=False) # Clear previous results

    # --- M/M/1 Widgets ---
    def _create_mm1_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="M/M/1 (Single Server, Exponential Service) Inputs")
        frame.grid_columnconfigure(1, weight=1)
        
        row_idx = 0
        # Using BaseGUI's create_input_row with unique label texts
        self.create_input_row(frame, row_idx, "MM1 Arrival Rate (\u03BB):", "5", "Average number of customers arriving per unit time.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "MM1 Service Rate (\u03BC):", "8", "Average number of customers a single server can serve per unit time.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "MM1 Number of Customers (n, for P_n):", "0", "Optional: Number of customers in the system for probability P_n. Leave blank if not needed.")
        row_idx += 1

        return frame

    # --- M/G/1 Widgets ---
    def _create_mg1_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="M/G/1 (Single Server, General Service) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        # Using BaseGUI's create_input_row with unique label texts
        self.create_input_row(frame, row_idx, "MG1 Arrival Rate (\u03BB):", "5", "Average number of customers arriving per unit time.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "MG1 Service Rate (\u03BC):", "8", "Average number of customers a single server can serve per unit time (1/E[S]).")
        row_idx += 1

        ttk.Label(frame, text="Service Time Distribution:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.mg1_dist_type_combobox = ttk.Combobox(
            frame,
            textvariable=self.mg1_dist_type_var,
            values=["Exponential", "Deterministic", "Uniform", "General (provide E[S^2])"],
            state="readonly"
        )
        self.mg1_dist_type_combobox.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.mg1_dist_type_combobox.bind("<<ComboboxSelected>>", self._on_mg1_distribution_selected)
        self.mg1_dist_selection_row = row_idx # Store row for combobox
        row_idx += 1

        # M/G/1 Specific fields for E[S^2] calculation or direct input
        # Manually create labels and entries to manage their visibility independently
        # Store references and add entries to self.input_fields for BaseGUI's clear_inputs
        
        # E[S^2]
        self.mg1_es2_label = ttk.Label(frame, text="E[S\u00b2] (Second Moment of Service Time):")
        self.mg1_es2_entry = ttk.Entry(frame, width=30)
        self.mg1_es2_entry.insert(0, "") # No default value
        self.input_fields[self.mg1_es2_key] = self.mg1_es2_entry # Register with BaseGUI's input_fields
        self.mg1_es2_input_row = row_idx
        row_idx += 1

        # Uniform Min
        self.mg1_uniform_min_label = ttk.Label(frame, text="Uniform Min Value (a):")
        self.mg1_uniform_min_entry = ttk.Entry(frame, width=30)
        self.mg1_uniform_min_entry.insert(0, "")
        self.input_fields[self.mg1_uniform_min_key] = self.mg1_uniform_min_entry
        self.mg1_uniform_min_input_row = row_idx
        row_idx += 1
        
        # Uniform Max
        self.mg1_uniform_max_label = ttk.Label(frame, text="Uniform Max Value (b):")
        self.mg1_uniform_max_entry = ttk.Entry(frame, width=30)
        self.mg1_uniform_max_entry.insert(0, "")
        self.input_fields[self.mg1_uniform_max_key] = self.mg1_uniform_max_entry
        self.mg1_uniform_max_input_row = row_idx
        row_idx += 1

        # Initial state: hide M/G/1 specific fields
        self.mg1_es2_label.grid_forget()
        self.mg1_es2_entry.grid_forget()
        self.mg1_uniform_min_label.grid_forget()
        self.mg1_uniform_min_entry.grid_forget()
        self.mg1_uniform_max_label.grid_forget()
        self.mg1_uniform_max_entry.grid_forget()
        
        self.mg1_dist_type_var.set("Exponential") # Default selection
        return frame

    def _on_mg1_distribution_selected(self, event=None):
        selected_dist = self.mg1_dist_type_var.get()
        logger.info(f"M/G/1 service time distribution selected: {selected_dist}")

        # Hide all M/G/1 specific fields
        if self.mg1_es2_label: self.mg1_es2_label.grid_forget()
        if self.mg1_es2_entry: self.mg1_es2_entry.grid_forget()
        if self.mg1_uniform_min_label: self.mg1_uniform_min_label.grid_forget()
        if self.mg1_uniform_min_entry: self.mg1_uniform_min_entry.grid_forget()
        if self.mg1_uniform_max_label: self.mg1_uniform_max_label.grid_forget()
        if self.mg1_uniform_max_entry: self.mg1_uniform_max_entry.grid_forget()

        # Show relevant fields based on selection
        if selected_dist == "General (provide E[S^2])":
            self.mg1_es2_label.grid(row=self.mg1_es2_input_row, column=0, padx=5, pady=5, sticky="w")
            self.mg1_es2_entry.grid(row=self.mg1_es2_input_row, column=1, padx=5, pady=5, sticky="ew")
        elif selected_dist == "Uniform":
            self.mg1_uniform_min_label.grid(row=self.mg1_uniform_min_input_row, column=0, padx=5, pady=5, sticky="w")
            self.mg1_uniform_min_entry.grid(row=self.mg1_uniform_min_input_row, column=1, padx=5, pady=5, sticky="ew")
            self.mg1_uniform_max_label.grid(row=self.mg1_uniform_max_input_row, column=0, padx=5, pady=5, sticky="w")
            self.mg1_uniform_max_entry.grid(row=self.mg1_uniform_max_input_row, column=1, padx=5, pady=5, sticky="ew")
        # For "Exponential" and "Deterministic", no extra fields are needed.


    # --- M/M/c Widgets ---
    def _create_mmc_widgets(self, parent_frame: ttk.Frame) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent_frame, text="M/M/c (Multiple Servers, Exponential Service) Inputs")
        frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        # Using BaseGUI's create_input_row with unique label texts
        self.create_input_row(frame, row_idx, "MMC Arrival Rate (\u03BB):", "15", "Average number of customers arriving per unit time.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "MMC Service Rate per Server (\u03BC):", "8", "Average number of customers EACH server can serve per unit time.")
        row_idx += 1
        self.create_input_row(frame, row_idx, "MMC Number of Servers (c):", "3", "The number of parallel servers in the system.")
        row_idx += 1

        return frame

    def calculate_queuing_metrics(self):
        self.display_result("Calculating queuing metrics...", is_error=False)
        selected_model = self.selected_model_var.get()

        if selected_model == "Select a Model":
            self.display_result("Please select a queuing model to calculate.", is_error=True)
            return

        try:
            output_message = [f"--- Results for {selected_model} ---"]
            
            if selected_model == "M/M/1 (Single Server, Exponential Service)":
                lambda_raw = self.get_input_value(self.mm1_lambda_key) # Use unique key
                mu_raw = self.get_input_value(self.mm1_mu_key)       # Use unique key
                n_raw = self.get_input_value(self.mm1_n_key)         # Use unique key

                is_valid, lambda_rate = self.validate_input(lambda_raw, 'positive_numeric', "Arrival Rate (\u03BB)")
                if not is_valid: raise ValueError(lambda_rate)
                
                is_valid, mu_rate = self.validate_input(mu_raw, 'positive_numeric', "Service Rate (\u03BC)")
                if not is_valid: raise ValueError(mu_rate)
                
                if lambda_rate >= mu_rate:
                    raise ValueError("System is unstable: Arrival rate (\u03BB) must be less than service rate (\u03BC).")


                rho = mm1_models.calculate_mm1_utilization(lambda_rate, mu_rate)
                L = mm1_models.calculate_mm1_avg_system_length(lambda_rate, mu_rate)
                Lq = mm1_models.calculate_mm1_avg_queue_length(lambda_rate, mu_rate)
                W = mm1_models.calculate_mm1_avg_waiting_time_system(lambda_rate, mu_rate)
                Wq = mm1_models.calculate_mm1_avg_waiting_time_queue(lambda_rate, mu_rate)

                output_message.append(f"Server Utilization (\u03C1): {self.format_percentage_output(rho * 100)}")
                output_message.append(f"Avg. Customers in System (L): {self.format_number_output(L, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Customers in Queue (Lq): {self.format_number_output(Lq, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in System (W): {self.format_number_output(W, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in Queue (Wq): {self.format_number_output(Wq, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                
                if n_raw: # Only calculate if n is provided
                    is_valid, n_val = self.validate_input(n_raw, 'non_negative_integer', "Number of Customers (n)")
                    if not is_valid: raise ValueError(n_val)
                    P_n = mm1_models.calculate_mm1_prob_n_customers(n_val, lambda_rate, mu_rate)
                    output_message.append(f"Probability of {n_val} Customers in System (P_{n_val}): {self.format_percentage_output(P_n * 100)}")

            elif selected_model == "M/G/1 (Single Server, General Service)":
                lambda_raw = self.get_input_value(self.mg1_lambda_key) # Use unique key
                mu_raw = self.get_input_value(self.mg1_mu_key)       # Use unique key

                is_valid, lambda_rate = self.validate_input(lambda_raw, 'positive_numeric', "Arrival Rate (\u03BB)")
                if not is_valid: raise ValueError(lambda_rate)
                
                is_valid, mu_rate = self.validate_input(mu_raw, 'positive_numeric', "Service Rate (\u03BC)")
                if not is_valid: raise ValueError(mu_rate)

                # TEMP DEBUGGING LINES - REMOVE THESE AFTER TESTING
                # print(f"DEBUG: M/G/1 -> lambda_rate: {lambda_rate}, type: {type(lambda_rate)}")
                # print(f"DEBUG: M/G/1 -> mu_rate: {mu_rate}, type: {type(mu_rate)}")
                # END TEMP DEBUGGING LINES

                if lambda_rate >= mu_rate:
                    raise ValueError("System is unstable: Arrival rate (\u03BB) must be less than service rate (\u03BC).")

                E_S2 = None
                dist_type = self.mg1_dist_type_var.get()

                if dist_type == "Exponential":
                    E_S2 = mg1_models.get_second_moment_service_time(mu_rate, 'exponential')
                elif dist_type == "Deterministic":
                    E_S2 = mg1_models.get_second_moment_service_time(mu_rate, 'deterministic')
                elif dist_type == "Uniform":
                    min_val_raw = self.get_input_value(self.mg1_uniform_min_key)
                    max_val_raw = self.get_input_value(self.mg1_uniform_max_key)

                    is_valid, min_val = self.validate_input(min_val_raw, 'numeric', "Uniform Min Value (a)")
                    if not is_valid: raise ValueError(min_val)
                    
                    is_valid, max_val = self.validate_input(max_val_raw, 'numeric', "Uniform Max Value (b)")
                    if not is_valid: raise ValueError(max_val)

                    if min_val >= max_val:
                        raise ValueError("Uniform Min Value (a) must be less than Max Value (b).")
                    E_S2 = mg1_models.get_second_moment_service_time(mu_rate, 'uniform', min_val=min_val, max_val=max_val)
                elif dist_type == "General (provide E[S^2])":
                    es2_raw = self.get_input_value(self.mg1_es2_key)
                    is_valid, E_S2 = self.validate_input(es2_raw, 'positive_numeric', "E[S\u00b2]")
                    if not is_valid: raise ValueError(E_S2)
                else:
                    raise ValueError("Invalid M/G/1 service time distribution selected.")

                rho = mg1_models.calculate_mg1_utilization(lambda_rate, mu_rate)
                Lq = mg1_models.calculate_mg1_avg_queue_length(lambda_rate, mu_rate, E_S2)
                L = mg1_models.calculate_mg1_avg_system_length(lambda_rate, mu_rate, E_S2)
                Wq = mg1_models.calculate_mg1_avg_waiting_time_queue(lambda_rate, mu_rate, E_S2)
                W = mg1_models.calculate_mg1_avg_waiting_time_system(lambda_rate, mu_rate, E_S2)

                output_message.append(f"Service Time Distribution: {dist_type}")
                if E_S2 is not None:
                     output_message.append(f"E[S\u00b2] (Second Moment of Service Time): {self.format_number_output(E_S2, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Server Utilization (\u03C1): {self.format_percentage_output(rho * 100)}")
                output_message.append(f"Avg. Customers in System (L): {self.format_number_output(L, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Customers in Queue (Lq): {self.format_number_output(Lq, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in System (W): {self.format_number_output(W, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in Queue (Wq): {self.format_number_output(Wq, DEFAULT_DECIMAL_PLACES_GENERAL)}")

            elif selected_model == "M/M/c (Multiple Servers, Exponential Service)":
                lambda_raw = self.get_input_value(self.mmc_lambda_key) # Use unique key
                mu_raw = self.get_input_value(self.mmc_mu_key)       # Use unique key
                c_raw = self.get_input_value(self.mmc_c_key)         # Use unique key

                is_valid, lambda_rate = self.validate_input(lambda_raw, 'positive_numeric', "Arrival Rate (\u03BB)")
                if not is_valid: raise ValueError(lambda_rate)
                
                is_valid, mu_rate = self.validate_input(mu_raw, 'positive_numeric', "Service Rate per Server (\u03BC)")
                if not is_valid: raise ValueError(mu_rate)
                
                is_valid, c = self.validate_input(c_raw, 'positive_integer', "Number of Servers (c)")
                if not is_valid: raise ValueError(c)

                if lambda_rate >= c * mu_rate:
                    raise ValueError(f"System is unstable: Arrival rate (\u03BB) must be less than (c * \u03BC) = {c * mu_rate}.")

                rho = mmc_models.calculate_mmc_utilization(lambda_rate, mu_rate, c)
                p_wait = mmc_models.calculate_mmc_prob_waiting(lambda_rate, mu_rate, c)
                Lq = mmc_models.calculate_mmc_avg_queue_length(lambda_rate, mu_rate, c)
                Wq = mmc_models.calculate_mmc_avg_waiting_time_queue(lambda_rate, mu_rate, c)
                L = mmc_models.calculate_mmc_avg_system_length(lambda_rate, mu_rate, c)
                W = mmc_models.calculate_mmc_avg_system_time(lambda_rate, mu_rate, c)

                output_message.append(f"Total Server Utilization (\u03C1): {self.format_percentage_output(rho * 100)}")
                output_message.append(f"Probability of Waiting (P_wait): {self.format_percentage_output(p_wait * 100)}")
                output_message.append(f"Avg. Customers in System (L): {self.format_number_output(L, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Customers in Queue (Lq): {self.format_number_output(Lq, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in System (W): {self.format_number_output(W, DEFAULT_DECIMAL_PLACES_GENERAL)}")
                output_message.append(f"Avg. Time in Queue (Wq): {self.format_number_output(Wq, DEFAULT_DECIMAL_PLACES_GENERAL)}")

            else:
                raise ValueError("Internal error: Unknown model selected.")

            self.display_result("\n".join(output_message), is_error=False)

        except ValueError as e:
            logger.warning(f"Input/Calculation Error for {selected_model}: {e}")
            self.display_result(f"Input Error: {e}", is_error=True)
        except ZeroDivisionError as e:
            logger.error(f"Division by zero error for {selected_model}: {e}", exc_info=True)
            self.display_result(f"Calculation Error: Division by zero (check inputs, especially for system stability).", is_error=True)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during {selected_model} calculation: {e}", exc_info=True)
            self.display_result(f"An unexpected error occurred: {e}", is_error=True)

    def clear_inputs(self):
        # Call the BaseGUI's clear_inputs, which uses self.input_fields
        super().clear_inputs()
        
        # Reset specific model combo boxes
        self.mg1_dist_type_var.set("Exponential")
        self.selected_model_var.set("Select a Model")

        # After clearing, re-run model selection to hide/show frames correctly
        self._on_model_selected()

        # Re-insert default values after clear (since BaseGUI's clear removes all)
        # Use the new, unique keys
        self.input_fields[self.mm1_lambda_key].insert(0, "5")
        self.input_fields[self.mm1_mu_key].insert(0, "8")
        self.input_fields[self.mm1_n_key].insert(0, "0")
        
        self.input_fields[self.mg1_lambda_key].insert(0, "5")
        self.input_fields[self.mg1_mu_key].insert(0, "8")

        # Note: The M/G/1 specific fields (E[S^2], uniform min/max) are handled by _on_model_selected
        # which will hide them, and they are automatically cleared by super().clear_inputs()
        # when their Entry widgets are registered in self.input_fields.
        
        self.input_fields[self.mmc_lambda_key].insert(0, "15") 
        self.input_fields[self.mmc_mu_key].insert(0, "8") 
        self.input_fields[self.mmc_c_key].insert(0, "3") 

        logger.info("QueuingCalculatorGUI inputs cleared and model selection reset.")


# Example usage (for testing QueuingCalculatorGUI in isolation)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Queuing Theory Calculator")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x700") # Adjusted height for Queuing

    test_parent_frame = ttk.Frame(root)
    test_parent_frame.pack(fill="both", expand=True)

    queuing_gui = QueuingCalculatorGUI(test_parent_frame, controller=None)
    queuing_gui.pack(fill="both", expand=True)

    root.mainloop()