# financial_calculator/config.py

import os

# --- Application Paths ---
# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMPARISON_SETS_FILE = os.path.join(DATA_DIR, 'comparison_sets.json')
APP_SETTINGS_FILE = os.path.join(DATA_DIR, 'app_settings.json')

# --- Application Settings ---
MAIN_WINDOW_TITLE = "Financial Calculator"
DEFAULT_WINDOW_WIDTH = 1100
DEFAULT_WINDOW_HEIGHT = 800

# Default display precision for various types of financial outputs
# These are general guidelines; specific GUI elements can override if needed.
DEFAULT_DECIMAL_PLACES_CURRENCY = 2
DEFAULT_DECIMAL_PLACES_PERCENTAGE = 4 # For rates like 0.0525 (5.25%)
DEFAULT_DECIMAL_PLACES_GENERAL = 6    # For general numerical results

# --- Theming Configuration ---
# Choose your desired ttk theme here.
# 'clam' is often recommended as a good base for extensive custom styling.
# Built-in themes include: 'default', 'alt', 'clam', 'classic', 'vista' (Windows only), 'xpnative' (Windows only), 'aqua' (macOS only).
# For more modern themes (like 'flatly', 'yeti', 'cosmo', etc.), install 'ttkthemes'.
TTK_THEME = 'clam' # Changed from 'vista' for better cross-platform consistency and custom style application

# Modern, professional color palette for UI elements
COLOR_PRIMARY_BACKGROUND = '#F0F4F8' # Light off-white/very light blue-gray for general backgrounds
COLOR_SECONDARY_BACKGROUND = '#FFFFFF' # Pure white for input areas, nested frames
COLOR_SIDEBAR_BACKGROUND = '#2C3E50' # Dark blue-gray for the sidebar
COLOR_TEXT_DARK = '#34495E' # Dark gray for text on light backgrounds
COLOR_TEXT_LIGHT = '#ECF0F1' # Light gray for text on dark backgrounds (sidebar)
COLOR_ACCENT_BLUE = '#3498DB' # A vibrant blue for primary buttons
COLOR_ACCENT_HOVER = '#2980B9' # Darker blue for button hover
COLOR_ACCENT_SELECTED = '#1ABC9C' # Turquoise for selected sidebar button
COLOR_ERROR_TEXT = '#E74C3C' # Red for error messages

# Font configuration
FONT_FAMILY_GENERAL = 'Segoe UI' # Modern, clean font (common on Windows)
                                 # Consider 'Arial', 'Helvetica', or 'TkDefaultFont' for broader cross-platform compatibility
FONT_SIZE_SMALL = 9
FONT_SIZE_MEDIUM = 10
FONT_SIZE_LARGE = 11
FONT_SIZE_XLARGE = 14 # For titles/main results

# --- Logging Settings ---
# Logging level for the application. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGGING_LEVEL = "INFO"
# Note: For session-based logging (cleared on exit), we won't define a persistent log file here.
# The logging setup in main.py will handle the in-memory or temporary file aspect.

# --- Other Constants (Add as needed) ---
# Example: Default values for input fields, or common labels
# DEFAULT_INTEREST_RATE = 0.05
# LABEL_PV = "Present Value:"