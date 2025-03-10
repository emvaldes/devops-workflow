#!/usr/bin/env python3

# Python File: ./lib/system_params.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File: ./lib/system_params.py

Description:
    System Parameter Management
    This module handles system-wide parameter management by loading runtime
    parameters from JSON configuration files and merging them with environment variables.

Core Features:
    - **Configuration Loading**: Reads parameters from `runtime-params.json`, `project-params.json`, and `default-params.json`.
    - **Environment Variable Management**: Dynamically sets system-wide environment variables.
    - **Validation and Error Handling**: Ensures required parameters are initialized before execution.

Usage:
    To load and initialize system parameters:
        python system_params.py

Dependencies:
    - os
    - json
    - logging
    - dotenv
    - pathlib
    - lib.configure_params (for JSON merging and validation)

Global Variables:
    - `SYSTEM_PARAMS` (dict): Loaded system-wide parameters.
    - `RUNTIME_PARAMS` (dict): Parameters dynamically merged at runtime.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to missing configuration files or invalid environment variables.
"""

FUNCTION_DOCSTRINGS = {
    "load_json_config": """
    Load environment variables from a JSON configuration file.

    Reads a JSON file and ensures its structure is valid before returning
    the parsed contents.

    Args:
        runtime_params_filepath (Path): The file path of the JSON configuration file.

    Raises:
        ValueError: If the JSON file is empty or has an invalid structure.
        RuntimeError: If the file cannot be read.

    Returns:
        dict: The parsed JSON data containing system parameters.
""",
    "get_runtime_variable": """
    Retrieve an environment variable safely, handling missing or empty values.

    This function fetches an environment variable and logs a warning if a required
    variable is missing or empty.

    Args:
        name (str): The name of the environment variable to retrieve.
        required (bool, optional): Whether the variable is mandatory. Defaults to False.

    Raises:
        RuntimeError: If there is an issue retrieving the environment variable.

    Returns:
        Optional[str]: The value of the environment variable, or None if it is missing.
""",
    "validate_runtime_params": """
    Validates the existence and content of the runtime parameters JSON file.

    This function checks whether the specified JSON file exists, is not empty,
    and contains valid JSON. It raises appropriate exceptions if any of the
    validation steps fail.

    Args:
        runtime_params_filepath (str or Path): The file path to the runtime parameters JSON file.

    Raises:
        FileNotFoundError: If the file specified by `runtime_params_filepath` does not exist.
        ValueError: If the file is empty or if it does not contain valid JSON.
"""
}

VARIABLE_DOCSTRINGS = {
    "SYSTEM_PARAMS": "Dictionary containing system-wide parameters loaded from configuration files.",
    "RUNTIME_PARAMS": "Dictionary containing runtime parameters dynamically merged at execution time.",
}
