#!/usr/bin/env python3

# Python File: ./tests/mocks/__init__.py

__package__ = "tests.mocks"
__module__ = "__init__"

__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: tests/mocks/__init__.py

Description:
    Initialization module for the `tests.mocks` package.

    This module ensures that the `tests/mocks/` directory is recognized as a Python package.
    It provides a structured framework for organizing mock objects and configurations used
    across the test suite.

Core Features:
    - **Package Initialization**: Enables `tests/mocks/` to function as a Python package.
    - **Mock Configuration Management**: Ensures that mock configuration loaders are accessible.
    - **Explicit Import Control**: Prevents unintended execution by requiring explicit mock imports.
    - **Dynamic Documentation Loading**: Loads and applies documentation dynamically to maintain
      structured docstrings across modules.

Usage:
    Modules within `tests/mocks/` should be explicitly imported when needed:
        from tests.mocks import config_loader
        config_loader.load_mock_requirements()

Important Notes:
    - This file **does not** automatically import submodules to prevent unnecessary execution.
    - Individual mock modules must be explicitly imported as required to maintain modularity.

Dependencies:
    - pathlib (for handling file paths)
    - sys (for managing system path imports)
    - lib.pydoc_loader (for loading documentation dynamically)

Example:
    ```python
    from tests.mocks import config_loader
    config_data = config_loader.load_mock_requirements()
    ```
"""

FUNCTION_DOCSTRINGS = {}

VARIABLE_DOCSTRINGS = {}
