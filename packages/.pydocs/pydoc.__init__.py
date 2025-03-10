#!/usr/bin/env python3

# Python File: ./packages/__init__.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: packages/__init__.py

Description:
    Packages Directory Initialization

    This module ensures that the `packages/` directory is recognized as a Python package.
    It establishes a structured framework for organizing submodules while maintaining
    explicit import control.

Core Features:
    - **Package Initialization**: Enables `packages/` to function as a Python package.
    - **Explicit Import Control**: Prevents unintended execution by requiring explicit submodule imports.
    - **Scalability**: Supports modular architecture by keeping dependencies well-structured.
    - **Path Management**: Ensures that `sys.path` includes the `packages/` directory for correct imports.

Usage:
    Modules and submodules within `packages/` should be explicitly imported:
        ```python
        from packages.appflow_tracer import tracing
        from packages.requirements import dependencies
        ```

Important Notes:
    - This file **does not** automatically import submodules to avoid unnecessary execution overhead.
    - Individual submodules must be explicitly imported when needed to maintain modularity.

Dependencies:
    - None (This module is solely responsible for initialization)

Example:
    To initialize logging from within the `appflow_tracer` package:
        ```python
        from packages.appflow_tracer import setup_logging
        CONFIGS = setup_logging()
        ```
"""

FUNCTION_DOCSTRINGS = {}

VARIABLE_DOCSTRINGS = {}
