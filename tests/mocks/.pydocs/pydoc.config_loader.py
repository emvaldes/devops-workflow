#!/usr/bin/env python3

# Python File: ./tests/mocks/config_loader.py

__package__ = "tests.mocks"
__module__ = "config_loader"

__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: tests/mocks/config_loader.py

Description:
    Mock Configuration Loader for Test Environments

    This module provides structured mock configuration files for testing purposes. It ensures
    that test cases operate with predictable configuration data by loading predefined JSON files
    (`mock_requirements.json` and `mock_installed.json`).

Core Features:
    - Loads `mock_requirements.json` for testing dependency policies.
    - Loads `mock_installed.json` for simulating installed packages.
    - Ensures missing configuration fields are automatically populated.
    - Prevents test failures due to missing or incomplete configuration files.

Expected Behavior:
    - If `mock_requirements.json` or `mock_installed.json` is missing, a default structure is used.
    - Test cases can rely on consistent configuration values.
    - Returns structured dictionaries with all required configuration fields.

Dependencies:
    - json (for reading and writing structured data)
    - pathlib (for managing file paths)

Usage:
    ```python
    from tests.mocks.config_loader import load_mock_requirements, load_mock_installed

    requirements = load_mock_requirements()
    installed = load_mock_installed()
    ```
"""

FUNCTION_DOCSTRINGS = {
    "load_mock_requirements": """
    Function: load_mock_requirements()

    Description:
        Loads and returns the contents of `mock_requirements.json`, ensuring
        that all required fields are present. If the file is missing, a default
        base configuration is returned.

    Parameters:
        - None

    Returns:
        - dict: A structured dictionary representing the mock requirements configuration.

    Behavior:
        - If `mock_requirements.json` exists, its contents are loaded.
        - If the file is missing, a predefined base configuration is used.
        - Ensures all required keys are present in the loaded data.

    Example:
        ```python
        config = load_mock_requirements()
        print(config["logging"]["enable"])  # True
        ```

    Notes:
        - Prevents test failures due to missing configuration files.
        - Populates default values for missing fields.
    """,

    "load_mock_installed": """
    Function: load_mock_installed()

    Description:
        Loads and returns the contents of `mock_installed.json`, ensuring
        that all required fields are present. If the file is missing, a default
        base configuration is returned.

    Parameters:
        - None

    Returns:
        - dict: A structured dictionary representing the mock installed package configuration.

    Behavior:
        - If `mock_installed.json` exists, its contents are loaded.
        - If the file is missing, a predefined base configuration is used.
        - Ensures all required keys are present in the loaded data.

    Example:
        ```python
        installed = load_mock_installed()
        print(installed["packages"]["installation"]["configs"])
        ```

    Notes:
        - Used for testing dependency installations and package state validation.
        - Guarantees test cases receive structured data.
    """
}

VARIABLE_DOCSTRINGS = {
    "MOCKS_DIR": """
    - Description: Absolute path to the `tests/mocks/` directory.
    - Type: Path
    - Usage: Used as the base directory for locating mock JSON files.
    """,

    "BASE_REQUIREMENTS_CONFIG": """
    - Description: Default structure for `mock_requirements.json` if missing.
    - Type: dict
    - Usage: Provides baseline settings for logging, tracing, and package installation.
    """,

    "BASE_INSTALLED_CONFIG": """
    - Description: Default structure for `mock_installed.json` if missing.
    - Type: dict
    - Usage: Mirrors `BASE_REQUIREMENTS_CONFIG` but includes package installation details.
    """
}
