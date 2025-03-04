#!/usr/bin/env python3

# File: ./lib/__init__.py
# Version: 0.1.0

"""
File Path: ./lib/__init__.py

Description:
    Library Package Initialization

    This file marks the `lib/` directory as a Python package, ensuring it can be
    properly imported within the framework. It may be used to initialize package-wide
    variables, import shared modules, or define commonly used utility functions.

Core Features:
    - **Package Initialization**: Ensures `lib/` is recognized as a Python package.
    - **Shared Module Accessibility**: Centralized location for utility imports.
    - **Potential for Future Expansions**: Can include package-wide configurations if needed.

Usage:
    Modules within `lib/` can be imported explicitly:
    ```python
    from lib import system_variables, file_utils
    ```

Important:
    - This file **does not** automatically import all submodules to prevent unnecessary overhead.
    - Individual submodules must be explicitly imported in other modules when required.

Dependencies:
    - None (This module serves as a package marker)

Example:
    ```python
    from lib import log_utils
    log_utils.log_message("Initialization successful.")
    ```
"""

# Package version
__version__ = "0.1.0"
