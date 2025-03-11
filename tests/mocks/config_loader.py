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

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

MOCKS_DIR = Path(__file__).resolve().parent  # `tests/mocks/`

def load_config(json_file: str) -> dict:
    """
    Load JSON configuration from the specified file.

    :param json_file: Path to the JSON configuration file.
    :return: Parsed JSON data as a dictionary.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return {}

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

# Determine the absolute path of the JSON file relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(SCRIPT_DIR, "mock_requirements.json")

# Load configuration
config_data = load_config(JSON_FILE_PATH)

# Apply transformation: Empty the "requirements" list
if "requirements" in config_data and isinstance(
    config_data["requirements"],
    list
):
    config_data["requirements"] = []

# Assign the transformed configuration
# Base structure for `mock_requirements.json` (policy settings)
BASE_REQUIREMENTS_CONFIG = config_data

# Base structure for `mock_installed.json` (installed packages)
BASE_INSTALLED_CONFIG = {
    "colors": BASE_REQUIREMENTS_CONFIG["colors"],
    "logging": BASE_REQUIREMENTS_CONFIG["logging"],
    "tracing": BASE_REQUIREMENTS_CONFIG["tracing"],
    "events": BASE_REQUIREMENTS_CONFIG["events"],
    "stats": BASE_REQUIREMENTS_CONFIG["stats"],
    "requirements": BASE_REQUIREMENTS_CONFIG["requirements"],
    "packages": BASE_REQUIREMENTS_CONFIG["packages"],
    "environment": BASE_REQUIREMENTS_CONFIG["environment"]
}

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
