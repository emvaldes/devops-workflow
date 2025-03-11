#!/usr/bin/env python3

# Python File: ./tests/mocks/config_loader.py

__package__ = "tests.mocks"
__module__ = "config_loader"

__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: tests/mocks/config_loader.py

Description:
    Mock Configuration Loader Module

    This module provides utilities for loading mock JSON-based configurations used
    in testing environments. It dynamically loads and processes configuration files,
    ensuring structured fallback handling and maintaining data integrity.

Core Features:
    - JSON Configuration Loading: Reads and validates structured JSON files.
    - Base Configuration Handling: Ensures required fields exist in loaded configurations.
    - Mock Data Processing: Allows simulated testing of dependency behaviors.
    - Error Handling: Captures and logs missing or malformed JSON files.

Usage:
    To load mock requirements:
        from tests.mocks.config_loader import load_mock_requirements
        mock_config = load_mock_requirements()

    To load installed package mock data:
        from tests.mocks.config_loader import load_mock_installed
        installed_config = load_mock_installed()

Dependencies:
    - sys - Handles system path modifications.
    - os - Provides file system utilities.
    - json - Loads and validates JSON-based configuration data.
    - pathlib - Ensures safe file path resolution.

Global Behavior:
    - Loads mock configuration data dynamically.
    - Ensures missing configuration fields are populated with default values.
    - Prevents errors due to missing or malformed configuration files.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to configuration loading errors.
"""

FUNCTION_DOCSTRINGS = {
    "load_config": """
    Function: load_config(json_file: str) -> dict

    Description:
        Loads JSON configuration from the specified file and returns the parsed data.

    Parameters:
        - json_file (str): The file path of the JSON configuration.

    Returns:
        - dict: Parsed JSON data as a dictionary.

    Error Handling:
        - Captures and prints errors if the file is missing or invalid.
""",
    "load_mock_requirements": """
    Function: load_mock_requirements() -> dict

    Description:
        Loads and returns the contents of `mock_requirements.json`, ensuring missing fields are populated.

    Parameters:
        - None

    Returns:
        - dict: The processed configuration dictionary with all necessary fields.

    Behavior:
        - Ensures a structured mock environment for package requirements.
        - Uses `BASE_REQUIREMENTS_CONFIG` as a fallback if the file is missing.
""",
    "load_mock_installed": """
    Function: load_mock_installed() -> dict

    Description:
        Loads and returns the contents of `mock_installed.json`, ensuring missing fields are populated.

    Parameters:
        - None

    Returns:
        - dict: The processed installed package configuration dictionary.

    Behavior:
        - Ensures structured test data for installed dependencies.
        - Uses `BASE_INSTALLED_CONFIG` as a fallback if the file is missing.
""",
    "main": """
    Function: main() -> None

    Description:
        Placeholder function for module execution.

    Parameters:
        - None

    Returns:
        - None
"""
}

VARIABLE_DOCSTRINGS = {
    "MOCKS_DIR": """
    - Description: Directory path containing mock configuration files.
    - Type: Path
    - Usage: Defines the base directory for loading mock JSON files.
    """,
    "SCRIPT_DIR": """
    - Description: Absolute path of the script directory.
    - Type: str
    - Usage: Used to resolve paths for JSON configuration files.
    """,
    "JSON_FILE_PATH": """
    - Description: Absolute path to the `mock_requirements.json` file.
    - Type: str
    - Usage: Specifies the location of the primary mock configuration file.
    """,
    "BASE_REQUIREMENTS_CONFIG": """
    - Description: The base mock requirements configuration loaded from `mock_requirements.json`.
    - Type: dict
    - Usage: Provides a structured policy configuration for testing environments.
    """,
    "BASE_INSTALLED_CONFIG": """
    - Description: The base installed package configuration derived from `BASE_REQUIREMENTS_CONFIG`.
    - Type: dict
    - Usage: Ensures consistent testing of installed package behaviors.
    """
}
