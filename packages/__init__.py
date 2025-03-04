#!/usr/bin/env python3

# File: ./packages/__init__.py
__version__ = "0.1.0"  ## Package version

"""
File Path: packages/__init__.py

Description:
    Packages Directory Initialization

    This file marks the `packages/` directory as a valid Python package. It ensures
    that all submodules and packages within `packages/` can be imported correctly
    without requiring additional path modifications.

Core Features:
    - **Package Initialization**: Enables `packages/` to be recognized as a valid Python package.
    - **Explicit Import Control**: Prevents unintended execution by requiring manual submodule imports.
    - **Scalability**: Supports a modular framework structure by keeping dependencies organized.

Usage:
    Modules within `packages/` should be imported explicitly as needed:
    ```python
    from packages.appflow_tracer import tracing
    from packages.requirements import dependencies
    ```

Important:
    - This file **does not** automatically import submodules to avoid unnecessary execution overhead.
    - Individual submodules must be explicitly imported by other modules when needed.

Dependencies:
    - None (This module solely serves as an initialization file)

Example:
    ```python
    from packages.appflow_tracer import setup_logging
    CONFIGS = setup_logging()
    ```
"""
