#!/usr/bin/env python3

# Python File: ./tests/conftest.py

__package__ = "tests"
__module__ = "conftest"

__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: tests/conftest.py

Description:
    PyTest Configuration Module for the Testing Framework

    This module provides shared test configurations, fixtures, and base configurations
    for testing various components of the system. It ensures consistency in test execution
    and provides reusable mock configurations.

Core Features:
    - Centralized Test Configuration: Establishes a standardized setup for PyTest execution.
    - Dynamic Package Configuration: Generates base configurations dynamically per module.
    - Mock Data Loading: Provides preconfigured test environments using `mock_requirements.json`
      and `mock_installed.json`.
    - Path Management: Ensures that project directories are properly included in `sys.path`.

Usage:
    This module is automatically loaded by PyTest when running tests within the `tests/` directory.

Dependencies:
    - pytest (for defining test fixtures)
    - pathlib (for handling file paths)
    - sys (for managing system path imports)
    - mocks.config_loader (for loading mock configurations)

Example:
    ```python
    def test_example(requirements_config):
        assert "logging" in requirements_config
    ```

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Error encountered in fixture loading or configuration processing.
"""

FUNCTION_DOCSTRINGS = {
    "get_base_config": """
    Function: get_base_config(package_name: str, module_name: str) -> dict

    Description:
        Generates a base configuration dynamically based on the given package and module names.

    Parameters:
        - package_name (str): The name of the package under test (e.g., "requirements").
        - module_name (str): The name of the module under test (e.g., "package_utils").

    Returns:
        - dict: A base configuration dictionary containing logging, tracing, events, stats,
                package installation settings, and environment details.

    Example:
        base_config = get_base_config("requirements", "package_utils")
        print(base_config["logging"]["package_name"])  # Output: "requirements"
    """,

    "requirements_config": """
    Function: requirements_config(request) -> dict

    Description:
        PyTest fixture for loading policy-based package configurations from `mock_requirements.json`.
        Ensures all required fields exist before returning the configuration.

    Parameters:
        - request (FixtureRequest): PyTest's request object to fetch module-specific attributes.

    Returns:
        - dict: A dictionary containing policy-based package configurations.

    Expected Behavior:
        - Loads configurations dynamically and merges them with default settings.
        - Converts package installation paths to `Path` objects.

    Example:
        def test_config(requirements_config):
            assert "logging" in requirements_config
    """,

    "installed_config": """
    Function: installed_config(request) -> dict

    Description:
        PyTest fixture for loading installed package configurations from `mock_installed.json`.
        Ensures alignment between `dependencies` (installed.json) and `requirements` (CONFIGS).

    Parameters:
        - request (FixtureRequest): PyTest's request object to fetch module-specific attributes.

    Returns:
        - dict: A dictionary containing installed package configurations.

    Expected Behavior:
        - Loads configurations dynamically and merges them with base settings.
        - Ensures `dependencies` field is populated correctly.
        - Converts package installation paths to `Path` objects.

    Example:
        def test_installed(installed_config):
            assert "dependencies" in installed_config
    """
}

VARIABLE_DOCSTRINGS = {
    "ROOT_DIR": """
    - Description: Root directory of the project, used to manage system path imports.
    - Type: Path
    - Usage: Ensures that test modules can access the required package directories.
    """,

    "MODULE_DOCSTRING": """
    - Description: Contains the module-level documentation for `conftest.py`.
    - Type: str
    - Usage: Defines module description, features, usage, and dependencies.
    """
}
