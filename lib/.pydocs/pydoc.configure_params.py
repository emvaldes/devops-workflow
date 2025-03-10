#!/usr/bin/env python3

# Python File: ./lib/configure_params.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
Overview
    The `configure_params.py` module manages system configuration by loading environment variables
    and runtime parameters from structured JSON configuration files.

Core Features:
    - Loads system parameters from predefined JSON sources.
    - Initializes and validates environment variables in `.env`.
    - Generates and maintains a runtime configuration file.
    - Dynamically updates values based on system settings.

Expected Behavior & Usage:
    Initializing Configuration:
        from lib.configure_params import main
        system_params, runtime_params = main()
"""

FUNCTION_DOCSTRINGS = {
    "load_json_sources": """
    Loads JSON data from multiple files and merges them if required.

    Parameters:
        filepaths (List[str]): List of JSON file paths to load.
        mode (str, optional): Determines if data should be merged or returned separately. Defaults to "merge".

    Returns:
        Union[Dict, Tuple[Dict]]: Merged dictionary or tuple of dictionaries based on mode.
""",
    "fetching_runtime_variables": """
    Extracts and structures runtime variables from system configuration files.

    Returns:
        Dict[str, Dict[str, Union[str, Dict[str, str]]]]: Organized runtime variables by section.
""",
    "initialize_env_file": """
    Ensures the `.env` file exists and is populated with valid environment variables.
""",
    "initialize_runtime_file": """
    Ensures the runtime parameters file exists and is updated with structured values.
""",
    "populate_env_file": """
    Generates and writes environment variables to the `.env` file from system configuration.

    Returns:
        bool: True if successful, False otherwise.
""",
    "populate_runtime_file": """
    Updates the runtime parameters JSON file with values extracted from system configurations and `.env`.

    Returns:
        bool: True if successful, False otherwise.
""",
    "validate_env_file": """
    Validates the `.env` file to ensure it exists and contains valid data.

    Returns:
        bool: True if valid, False otherwise.
""",
    "validate_runtime_file": """
    Validates the runtime parameters JSON file to ensure it is correctly structured.

    Returns:
        bool: True if valid, False otherwise.
""",
    "main": """
    Orchestrates the initialization and validation of system configurations.

    Returns:
        Tuple[Dict, Dict]: Loaded system parameters and runtime parameters.
"""
}

VARIABLE_DOCSTRINGS = {
    "project_root": "Root directory of the project.",
    "env_filepath": "Path to the `.env` file storing environment variables.",
    "runtime_params_filename": "Filename of the runtime parameters JSON file.",
    "system_params_filename": "Filename of the system parameters JSON file.",
    "runtime_params_filepath": "Path to the runtime parameters JSON file.",
    "system_params_filepath": "Path to the system parameters JSON file.",
    "system_params_listing": "List of paths to system configuration JSON files."
}
