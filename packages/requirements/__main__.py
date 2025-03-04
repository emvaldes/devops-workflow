#!/usr/bin/env python3

# File: ./packages/requirements/__main__.py
__version__ = "0.1.0"  ## Package version

"""
File Path: packages/requirements/__main__.py

Description:
    Requirements Package Entry Point

    This file serves as the execution entry point for the `requirements` package when run
    in standalone mode. It initializes and runs the dependency management system by calling
    the `main()` function from `dependencies.py`.

Core Features:
    - **Standalone Execution**: Enables `python -m packages.requirements` execution.
    - **Dependency Management**: Calls `main()` from `dependencies.py` to handle dependencies.
    - **Modular Design**: Supports both standalone execution and direct function imports.

Usage:
    To execute the `requirements` package as a standalone script:
    ```bash
    python -m packages.requirements
    ```

Dependencies:
    - dependencies (for managing package dependencies)

Example:
    ```bash
    python -m packages.requirements
    ```
"""

# Import the main function from dependencies.py
from packages.requirements.dependencies import main

if __name__ == "__main__":
    main()
