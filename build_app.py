import subprocess
import os
import shutil
import sys
import logging

# Set up basic logging
# Keeping it at WARNING now as requested, but set to INFO temporarily for debugging if needed
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_build():
    """
    Runs the PyInstaller command to build the executable.
    """
    # Define variables for the build
    script_name = "main_app.py"
    exe_name = "Financial Calculator"
    icon_file = "app_icon.ico"
    config_file = "config.py"

    # Define the output directories
    dist_dir = "dist"
    build_dir = "build"
    spec_file_1 = f"{script_name.replace('.py', '')}.spec"
    spec_file_2 = f"{exe_name}.spec"

    # Get the directory where build_app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    logger.info(f"Working directory set to: {os.getcwd()}") # This will still show as INFO

    # --- Clean previous builds ---
    logger.info("Cleaning previous build artifacts...") # This will still show as INFO
    for directory in [build_dir, dist_dir]:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                logger.info(f"Removed directory: {directory}") # This will still show as INFO
            except OSError as e:
                logger.error(f"Error removing directory {directory}: {e}")
                sys.exit(1)

    for spec in [spec_file_1, spec_file_2]:
        if os.path.exists(spec):
            try:
                os.remove(spec)
                logger.info(f"Removed spec file: {spec}") # This will still show as INFO
            except OSError as e:
                logger.error(f"Error removing spec file {spec}: {e}")
                sys.exit(1)
    logger.info("Cleaning complete.") # This will still show as INFO

    # Determine the correct path separator for --add-data
    data_sep = ';' if sys.platform == 'win32' else ':'

    # --- Construct the PyInstaller command ---
    command = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        f"--icon={icon_file}",
        f"--add-data={config_file}{data_sep}.",
        f"--add-data=gui{data_sep}gui",
        f"--add-data=mathematical_functions{data_sep}mathematical_functions",
        f"--add-data=utils{data_sep}utils",
        f"--name={exe_name}",
        script_name,
        "--log-level", "WARN", # Keep this for less PyInstaller verbose output
        "--collect-all", "numpy_financial",
        "--collect-all", "scipy",
        "--collect-data", "tkinter",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "matplotlib.backends.backend_tkagg",
        "--hidden-import", "matplotlib.pyplot"
    ]
    logger.info(f"Starting PyInstaller build with command: {' '.join(command)}") # This will still show as INFO

    # --- Run PyInstaller ---
    try:
        process = subprocess.run(command, check=True, capture_output=False, text=True)

        logger.info("PyInstaller build SUCCESSFUL!") # This will still show as INFO
        final_exe_name = f"{exe_name}{'.exe' if sys.platform == 'win32' else ''}"
        logger.info(f"Executable located in the '{dist_dir}' folder: {final_exe_name}") # This will still show as INFO

    except subprocess.CalledProcessError as e:
        logger.error(f"!!! PyInstaller build FAILED !!!")
        logger.error(f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("PyInstaller command not found. Please ensure PyInstaller is installed and in your PATH.")
        logger.info("You can install it using: pip install pyinstaller") # This will still show as INFO
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_build()