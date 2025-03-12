#!/usr/bin/env python3

# File: ./tests/mocks/config_loader.py

__package__ = "tests.mocks"
__module__ = "config_loader"

__version__ = "0.1.0"  # Module version

# Standard library imports - Core system and OS interaction modules
import sys
import os

# Standard library imports - Utility module
import json

# Standard library imports - File system-related module
from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_params as params_utils

MOCKS_DIR = Path(__file__).resolve().parent  # `tests/mocks/`

def load_mock_requirements() -> dict:

    file_path = MOCKS_DIR / "mock_requirements.json"
    if not file_path.exists():
        return BASE_REQUIREMENTS_CONFIG  # Return base config if file is missing

    with open(file_path, "r") as file:
        data = json.load(file)

    # Ensure base structure is maintained
    for key in BASE_REQUIREMENTS_CONFIG:
        data.setdefault(key, BASE_REQUIREMENTS_CONFIG[key])

    return data

def load_mock_installed() -> dict:

    file_path = MOCKS_DIR / "mock_installed.json"
    if not file_path.exists():
        return BASE_INSTALLED_CONFIG  # Return base config if file is missing

    with open(file_path, "r") as file:
        data = json.load(file)

    # Ensure base structure is maintained
    for key in BASE_INSTALLED_CONFIG:
        data.setdefault(key, BASE_INSTALLED_CONFIG[key])

    return data

def main() -> None:
    pass

validation_schema = {
    "requirements": [{}]  # Validate that the 'requirements' field is a list
}

# Determine the absolute path of the JSON file relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILEPATH=os.path.join(SCRIPT_DIR, "mock_requirements.json")
INSTALLED_FILEPATH=os.path.join(SCRIPT_DIR, "mock_installed.json")

# Load Requirements configuration
requirements_config = params_utils.load_json_config(
    json_filepath=REQUIREMENTS_FILEPATH,
    validation_schema=validation_schema
)
# print(f'Config Data:\n{json.dumps(requirements_config, indent=4)}')

if requirements_config:
    if "requirements" in requirements_config and isinstance(
        requirements_config["requirements"],
        list
    ):
        requirements_config["requirements"] = []

# Base structure for `mock_requirements.json` (policy settings)
BASE_REQUIREMENTS_CONFIG = requirements_config

# Load Requirements configuration
installed_config = params_utils.load_json_config(
    json_filepath=INSTALLED_FILEPATH,
    validation_schema=validation_schema
)
# print(f'Config Data:\n{json.dumps(installed_config, indent=4)}')

if installed_config:
    if "requirements" in installed_config and isinstance(
        installed_config["requirements"],
        list
    ):
        installed_config["requirements"] = []

# Base structure for `mock_installed.json` (installed packages)
BASE_INSTALLED_CONFIG = installed_config

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
