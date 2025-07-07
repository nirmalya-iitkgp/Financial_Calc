import logging
# Configure the root logger to output INFO messages and above
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

import tkinter as tk
from tkinter import ttk, messagebox
import config

# Import all individual GUI modules
from gui.tvm_gui import TVMGUI
from gui.fixed_income_gui import FixedIncomeGUI
from gui.derivatives_gui import DerivativesGUI
from gui.equity_portfolio_gui import EquityPortfolioGUI
from gui.business_accounting_gui import BusinessAccountingGUI
from gui.general_tools_gui import GeneralToolsGUI
from gui.commodity_real_estate_gui import CommodityAndRealEstateFinanceGUI
from gui.private_markets_credit_gui import PrivateMarketsAndCreditRiskGUI
from gui.yield_curve_gui import YieldCurveGUI 
from gui.queuing_calculator_gui import QueuingCalculatorGUI
from gui.operations_finance_gui import OperationsFinanceGUI

# Get a logger for this module (main_app.py)
logger = logging.getLogger(__name__)

class MainApplication(tk.Tk):
    """
    The main application class that creates the root window and integrates
    all individual calculator GUIs into a side-bar navigation interface.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Financial Calculator Suite")
        # Adjust geometry for sidebar layout (wider to accommodate sidebar + content)
        self.geometry("1100x800")

        # Configure the theme
        self._setup_style()

        # --- UI Layout Changes Start Here ---
        # Create a main container frame to hold both sidebar and content
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True) # Container fills the root window

        # Configure grid for the container: 1 row, 2 columns
        # Column 0 for sidebar (fixed width), Column 1 for content (expands)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=0) # Sidebar column
        self.container.grid_columnconfigure(1, weight=1) # Content column (expands)

        # Create sidebar frame
        # relief and borderwidth give a visual separation
        self.sidebar_frame = ttk.Frame(self.container, width=200, relief="raised", borderwidth=1)
        self.sidebar_frame.grid(row=0, column=0, sticky="nswe") # Place in column 0, expands N,S,W,E

        # Create content frame where calculator GUIs will be displayed
        self.content_frame = ttk.Frame(self.container)
        self.content_frame.grid(row=0, column=1, sticky="nswe") # Place in column 1, expands N,S,W,E
        self.content_frame.grid_rowconfigure(0, weight=1) # Make content frame's internal row expand
        self.content_frame.grid_columnconfigure(0, weight=1) # Make content frame's internal column expand

        # Store references to your GUI frames and sidebar buttons
        self.frames = {}
        self.calculator_buttons = {} # To hold references to sidebar buttons for highlighting

        # Define the list of calculator modules
        self.calculator_modules = [
            ("Time Value of Money", TVMGUI),
            ("Bonds", FixedIncomeGUI),
            ("Derivatives", DerivativesGUI),
            ("Equity & Portfolio", EquityPortfolioGUI),
            ("Business & Accounting", BusinessAccountingGUI),
            ("Commodity & Real Estate", CommodityAndRealEstateFinanceGUI),
            ("Private Mkts & Credit Risk", PrivateMarketsAndCreditRiskGUI),
            ("Yield Curve Models", YieldCurveGUI), 
            ("Queuing Theory", QueuingCalculatorGUI),
            ("Operations Finance", OperationsFinanceGUI),
            ("General Tools", GeneralToolsGUI),
        ]

        # Add calculator GUIs to content frame and create sidebar buttons
        self._add_calculator_frames_and_buttons()

        # Show the first calculator by default when the application starts
        if self.calculator_modules:
            first_module_name = "General Tools" # self.calculator_modules[0][0]
            self._show_frame(first_module_name)
            self._highlight_button(first_module_name) # Highlight its button

        # --- UI Layout Changes End Here ---

        # Set up a protocol for handling window closing (existing functionality)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("MainApplication initialized with sidebar UI.")

    def _setup_style(self):
        """Applies a modern ttk style to the application and customizes sidebar buttons."""
        style = ttk.Style(self)
        try:
            # Use theme from config.py as defined
            style.theme_use(config.TTK_THEME)
            logger.info(f"Applied ttk theme: {config.TTK_THEME}")
        except tk.TclError:
            logger.warning(f"Theme '{config.TTK_THEME}' not found, falling back to 'clam'.")
            style.theme_use('clam') # Fallback if theme from config is not available

        # Customize general widget styles (existing)
        style.configure('TFrame', background='#f0f0f0') # Lighter background for frames
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TEntry', font=('Arial', 10))
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0', font=('Arial', 11, 'bold'))

        # --- New Sidebar Button Styles ---
        style.configure('Sidebar.TButton',
                        background='#4a7abc', # Blueish background
                        foreground='white',   # White text
                        font=('Arial', 11, 'bold'),
                        padding=[10, 10],     # Add padding
                        relief='flat')        # Flat look
        style.map('Sidebar.TButton',
                  background=[('active', '#5b8cdb'), ('!disabled', '#4a7abc')], # Darker blue on hover
                  foreground=[('active', 'white'), ('!disabled', 'white')])

        # Styling for selected button
        style.configure('Selected.Sidebar.TButton',
                        background='#1e5799', # Even darker blue for selected
                        foreground='white',
                        font=('Arial', 11, 'bold'),
                        padding=[10, 10],
                        relief='solid',      # Solid border or deeper effect
                        borderwidth=2)
        style.map('Selected.Sidebar.TButton',
                  background=[('active', '#1e5799'), ('!disabled', '#1e5799')],
                  foreground=[('active', 'white'), ('!disabled', 'white')])
        # --- End New Sidebar Button Styles ---


    # --- New Methods for Sidebar UI ---
    def _add_calculator_frames_and_buttons(self):
        """
        Creates instances of all calculator GUIs, places them in the content_frame
        (initially hidden), and creates their corresponding buttons in the sidebar.
        """
        button_frame = ttk.Frame(self.sidebar_frame)
        button_frame.pack(fill="both", expand=True, pady=10) # Pack into sidebar_frame
        button_frame.grid_columnconfigure(0, weight=1) # Make buttons expand horizontally

        for i, (module_name, gui_class) in enumerate(self.calculator_modules):
            # Create GUI instance inside the content_frame
            frame_instance = gui_class(self.content_frame, controller=self)
            # Use grid to place the frame instance, making it fill its cell
            frame_instance.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            frame_instance.grid_remove() # Initially hide all frames

            self.frames[module_name] = frame_instance # Store reference to the frame instance
            logger.info(f"Loaded GUI for: {module_name}")

            # Create sidebar button for this module
            button = ttk.Button(button_frame,
                                text=module_name,
                                command=lambda name=module_name: self._show_frame(name),
                                style='Sidebar.TButton') # Apply custom sidebar style
            button.grid(row=i, column=0, sticky="ew", padx=10, pady=5) # Place button in button_frame
            self.calculator_buttons[module_name] = button # Store button reference for highlighting

    def _show_frame(self, frame_name: str):
        """
        Shows the specified calculator frame in the content area and hides all others.
        Also updates the sidebar button highlight.
        """
        frame = self.frames.get(frame_name)
        if frame:
            # Hide all other frames in the content_frame
            for name, other_frame in self.frames.items():
                if other_frame is not frame:
                    other_frame.grid_remove() # Use grid_remove for grid layout

            # Show the selected frame
            frame.grid() # Make visible using grid

            # Highlight the corresponding button in the sidebar
            self._highlight_button(frame_name)

            logger.info(f"Displayed calculator: {frame_name}")
        else:
            logger.error(f"Attempted to show non-existent frame: {frame_name}")
            messagebox.showerror("UI Error", f"Calculator module '{frame_name}' not found.")

    def _highlight_button(self, active_button_name: str):
        """Highlights the active button in the sidebar and unhighlights others."""
        for name, button in self.calculator_buttons.items():
            if name == active_button_name:
                button.config(style='Selected.Sidebar.TButton') # Apply selected style
            else:
                button.config(style='Sidebar.TButton') # Apply default sidebar style
    # --- End New Methods ---


    # --- Existing Functionality (Copied as-is) ---
    # _add_calculator_tab has been replaced by _add_calculator_frames_and_buttons
    # so this method is effectively removed from the new structure.

    def _on_closing(self):
        """
        Handles the window closing event, prompting the user for confirmation.
        """
        if messagebox.askokcancel("Quit", "Do you want to quit the Financial Calculator Suite?"):
            logger.info("Application closed by user.")
            self.destroy()

# Main entry point for the application
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()