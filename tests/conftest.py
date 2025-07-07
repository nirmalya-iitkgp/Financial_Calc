# tests/conftest.py

import sys
from pathlib import Path

# Get the parent directory of the 'tests' directory (which is your project root)
# This assumes 'mathematical_functions' and 'tests' are direct siblings
project_root = Path(__file__).resolve().parent.parent

# Add the project root to sys.path
# This makes the 'mathematical_functions' package discoverable
sys.path.insert(0, str(project_root))

# You can also use a pytest hook for more explicit control,
# but for simple path modification, direct execution is fine.
# For example, if you wanted to do this only once per test session:
# def pytest_sessionstart(session):
#     project_root = Path(__file__).resolve().parent.parent
#     sys.path.insert(0, str(project_root))