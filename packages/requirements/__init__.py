#!/usr/bin/env python3

# File: ./packages/requirements/__init__.py
# Version: 0.1.0

"""
File Path: packages/requirements/__init__.py

Description:
    Requirements Package Initialization

    This file defines the `requirements` package and ensures it is properly recognized
    as a Python package. It provides an entry point for managing dependencies by exposing
    the `main` function from `dependencies.py`.

Core Features:
    - **Package Initialization**: Marks `requirements/` as a valid Python package.
    - **Dependency Management**: Exposes `main()` from `dependencies.py` for handling dependencies.
    - **Explicit Module Control**: Prevents unintended imports by requiring explicit calls.

Usage:
    To execute the dependencies management function:
    ```python
    from packages.requirements import main
    main()
    ```

Important:
    - This file **does not** execute any logic automatically.
    - The `main()` function must be explicitly invoked when needed.

Dependencies:
    - dependencies (for handling package dependency management)

Example:
    ```python
    from packages.requirements import main
    main()
    ```
"""

# Package version
__version__ = "0.1.0"

# Import the main function from dependencies.py for package-level execution
from packages.requirements.dependencies import main

# Explicitly define available functions
__all__ = ["main"]
