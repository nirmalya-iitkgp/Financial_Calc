# financial_calculator/gui/base_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
from typing import Union
import re

# Import the config file
import config # <--- ADDED: Import config

from config import (
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, MAIN_WINDOW_TITLE,
    DEFAULT_DECIMAL_PLACES_CURRENCY, DEFAULT_DECIMAL_PLACES_PERCENTAGE, DEFAULT_DECIMAL_PLACES_GENERAL
)
from utils.validation import (
    validate_numeric_input, validate_positive_numeric_input,
    validate_non_negative_numeric_input, validate_percentage_input,
    validate_list_input,
    validate_numeric_range,
    validate_positive_integer_input,
    validate_non_negative_integer_input
)
from utils.helper_functions import format_currency, format_percentage, format_number

# Set up logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseGUI(ttk.Frame):
    """
    Base class for all financial calculator GUI modules.
    Provides common UI elements, a scrollable frame, and utility methods.
    """
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.controller = controller

        self.input_fields = {}
        self.calculation_result_label = None

        # --- Apply the TTK Theme from config.py ---
        # It's best to set the theme once, typically at the root window level (e.g., in App.py).
        # However, if BaseGUI is the primary entry point for individual module testing,
        # or if you want to ensure it's always set when a BaseGUI instance is created,
        # placing it here works. Just be aware it might re-apply if multiple BaseGUI instances are made.
        # A more robust solution for an app with a main App.py is to apply it there once.
        style = ttk.Style()
        try:
            style.theme_use(config.TTK_THEME) # <--- Using the theme from config.py
            logger.info(f"Applied ttk theme: {config.TTK_THEME}")
        except tk.TclError as e:
            logger.warning(f"Could not apply theme '{config.TTK_THEME}': {e}. Falling back to 'clam'.")
            style.theme_use('clam') # Fallback if the theme isn't found
        # --- End Theme Application ---

        self._setup_scrollable_frame()
        self._create_common_widgets(self.scrollable_frame)

        logger.info(f"Initialized BaseGUI for {self.__class__.__name__}")

    def _setup_scrollable_frame(self):
        style = ttk.Style()
        frame_bg = style.lookup('TFrame', 'background')

        self.canvas = tk.Canvas(self, borderwidth=0, background=frame_bg)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            if sys.platform == "darwin":
                self.canvas.yview_scroll(int(-1*(event.delta/60)), "units")
            elif sys.platform.startswith("win"):
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def _create_common_widgets(self, parent_frame):
        self.result_frame = ttk.LabelFrame(parent_frame, text="Calculation Result / Messages")
        self.result_frame.grid(row=99, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        parent_frame.grid_columnconfigure(0, weight=1)

        self.calculation_result_label = ttk.Label(self.result_frame, text="Enter values and click Calculate.", wraplength=DEFAULT_WINDOW_WIDTH - 60)
        self.calculation_result_label.pack(padx=5, pady=5, fill="x", expand=True)

        self.common_buttons_frame = ttk.Frame(parent_frame)
        self.common_buttons_frame.grid(row=100, column=0, columnspan=2, pady=5)

        self.clear_button = ttk.Button(self.common_buttons_frame, text="Clear All", command=self.clear_inputs)
        self.clear_button.pack(side="left", padx=5)

        self.calculate_button = ttk.Button(self.common_buttons_frame, text="Calculate (Override Me)", command=self.calculate)
        self.calculate_button.pack(side="left", padx=5)

    def create_input_row(self, parent_frame, row, label_text, default_value="", tooltip_text=""):
        """
        Helper method to create a label and an Entry widget for input.
        Stores the Entry widget in self.input_fields.

        Args:
            parent_frame (tk.Widget): The frame to place the widgets in.
            row (int): The grid row for these widgets.
            label_text (str): The text for the label.
            default_value (str): Initial value for the Entry.
            tooltip_text (str): Tooltip message for the entry field.
        """
        label = ttk.Label(parent_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        entry = ttk.Entry(parent_frame, width=30)
        entry.insert(0, str(default_value))
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        
        # Convert label to lowercase, replace non-alphanumeric with spaces,
        # then consolidate multiple spaces to single underscores, and strip leading/trailing underscores.
        field_key = label_text.lower()
        field_key = re.sub(r'[^a-z0-9]+', ' ', field_key).strip() # Replace non-alphanumeric with single space, strip outer spaces
        field_key = field_key.replace(' ', '_') # Replace remaining spaces with underscores
        
        self.input_fields[field_key] = entry

        if tooltip_text:
            logger.debug(f"Tooltip for '{label_text}': '{tooltip_text}' (not implemented in BaseGUI)")

        return entry

    def get_input_value(self, field_key: str) -> str:
        entry = self.input_fields.get(field_key)
        if entry:
            return entry.get()
        logger.warning(f"Attempted to get value from non-existent input field: {field_key}")
        return ""

    def display_result(self, message: str, is_error: bool = False):
        if self.calculation_result_label:
            self.calculation_result_label.config(text=message)
            if is_error:
                self.calculation_result_label.config(foreground="red")
                logger.error(f"GUI Error: {message}")
            else:
                self.calculation_result_label.config(foreground="black")
            logger.info(f"GUI Result: {message}")
        else:
            logger.warning(f"Result label not initialized. Message: {message}")

    def clear_inputs(self):
        for field_key, entry_widget in self.input_fields.items():
            entry_widget.delete(0, tk.END)
        self.display_result("Inputs cleared.")
        logger.info(f"Cleared inputs for {self.__class__.__name__}")

    def calculate(self):
        self.display_result("Calculation logic not implemented for this module.", is_error=True)
        logger.warning("BaseGUI's calculate method called. This should be overridden.")

    def validate_input(self, value: str, validation_type: str, field_name: str = "Input") -> tuple[bool, Union[float, str]]:
        """
        Validates a single input string using a specified validation type.
        Delegates to functions in utils.validation.
        """
        if validation_type == 'numeric':
            return validate_numeric_input(value, field_name)
        elif validation_type == 'positive_numeric':
            return validate_positive_numeric_input(value, field_name)
        elif validation_type == 'non_negative_numeric':
            return validate_non_negative_numeric_input(value, field_name)
        elif validation_type == 'percentage':
            # Note: This just validates it's a number. Range check (0-100)
            # should be done with 'numeric_range_0_100' or in calculation logic.
            return validate_percentage_input(value, field_name)
        elif validation_type == 'numeric_range_0_100': # <--- ADDED: Handle this specific range
            return validate_numeric_range(value, 0, 100, field_name)
        elif validation_type == 'positive_integer': # <--- ADDED: For the Current Year input
            return validate_positive_integer_input(value, field_name)
        elif validation_type == 'non_negative_integer': # <--- for including 0
            return validate_non_negative_integer_input(value, field_name)
        else:
            logger.error(f"Unknown validation type requested: {validation_type}")
            return False, "Internal error: Invalid validation type."

    def validate_input_list(self, input_str: str, expected_type: str, field_name: str) -> tuple[bool, Union[list, str]]:
        """
        Validates a comma-separated string of inputs, delegating to utils.validation.validate_list_input.
        """
        return validate_list_input(input_str, expected_type, field_name)

    def format_currency_output(self, amount: Union[float, int], currency_symbol: str = "$", decimal_places: int = DEFAULT_DECIMAL_PLACES_CURRENCY) -> str:
        return format_currency(amount, currency_symbol, decimal_places)

    def format_percentage_output(self, value: Union[float, int], decimal_places: int = DEFAULT_DECIMAL_PLACES_PERCENTAGE) -> str:
        return format_percentage(value, decimal_places)

    def format_number_output(self, value: Union[float, int], decimal_places: int = DEFAULT_DECIMAL_PLACES_GENERAL) -> str:
        return format_number(value, decimal_places)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("BaseGUI Test")
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")

    # --- REMOVED: Theme setting is now handled by BaseGUI's __init__ method ---
    # style = ttk.Style()
    # style.theme_use('clam')

    base_frame = BaseGUI(root) # <--- Theme applied here when BaseGUI is instantiated
    base_frame.pack(fill="both", expand=True)

    base_frame.create_input_row(base_frame.scrollable_frame, 0, "Dummy Input 1 (Test):", "100")
    base_frame.create_input_row(base_frame.scrollable_frame, 1, "Dummy Input 2 %:", "0.05")
    base_frame.create_input_row(base_frame.scrollable_frame, 2, "Another Value!!", "5")
    
    # Test for list input
    base_frame.create_input_row(base_frame.scrollable_frame, 3, "Comma Separated Data:", "10,20,30,40")
    base_frame.create_input_row(base_frame.scrollable_frame, 4, "Invalid List Data:", "10,abc,30")
    
    for i in range(5, 30): # Adjust row start to accommodate new fields
        base_frame.create_input_row(base_frame.scrollable_frame, i, f"Long Content Row {i} (Extra):", f"{i*10}")

    def test_calculate():
        val1_str = base_frame.get_input_value("dummy_input_1_test")
        val2_str = base_frame.get_input_value("dummy_input_2")
        val3_str = base_frame.get_input_value("another_value")
        list_data_str = base_frame.get_input_value("comma_separated_data")
        invalid_list_data_str = base_frame.get_input_value("invalid_list_data")
        
        is_valid1, num1 = base_frame.validate_input(val1_str, 'numeric', "Dummy Input 1")
        is_valid2, num2 = base_frame.validate_input(val2_str, 'percentage', "Dummy Input 2")
        
        # Test the new list validation
        is_valid_list, data_list = base_frame.validate_input_list(list_data_str, 'numeric', "Comma Separated Data")
        is_valid_invalid_list, invalid_data_list = base_frame.validate_input_list(invalid_list_data_str, 'numeric', "Invalid List Data")

        output_messages = []
        is_all_successful = True

        if is_valid1 and is_valid2:
            try:
                # Assuming num2 is a percentage like 0.05 (for 5%), convert to 5.0 for display
                result = float(num1) * float(num2)
                output_messages.append(f"Calculation: {num1} * {base_frame.format_percentage_output(num2 * 100)} = {base_frame.format_currency_output(result)}")
            except Exception as e:
                output_messages.append(f"Error during calculation: {e}")
                is_all_successful = False
        else:
            if not is_valid1: output_messages.append(str(num1))
            if not is_valid2: output_messages.append(str(num2))
            is_all_successful = False
        
        if is_valid_list:
            output_messages.append(f"Validated List (Numeric): {data_list} (Sum: {sum(data_list)})")
        else:
            output_messages.append(f"List Validation Error (Numeric): {data_list}") # data_list will be the error message here
            is_all_successful = False
        
        if is_valid_invalid_list:
            output_messages.append(f"Validated Invalid List (Unexpected Success): {invalid_data_list}")
            is_all_successful = False # This case should ideally fail
        else:
            output_messages.append(f"List Validation Error (Expected Failure): {invalid_data_list}") # invalid_data_list will be the error message here

        base_frame.display_result("\n".join(output_messages), is_error=not is_all_successful)


    base_frame.calculate_button.config(text="Test Calculate", command=test_calculate)

    root.mainloop()