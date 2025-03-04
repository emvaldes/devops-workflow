#!/usr/bin/env python3

"""
File Path: ./scripts/__init__.py

Description:
    Scripts Package Initialization

    This file marks the `scripts/` directory as a valid Python package. It ensures
    that standalone scripts within the framework can be properly imported and executed.

Core Features:
    - **Package Initialization**: Enables `scripts/` to be recognized as a Python package.
    - **Modular Script Management**: Allows standalone scripts to be structured and executed efficiently.
    - **Future Expansion**: Can be extended to initialize common utilities if needed.

Usage:
    Scripts within `scripts/` should be explicitly imported when needed:
    ```python
    from scripts import some_script
    some_script.execute()
    ```

Important:
    - This file **does not** automatically import submodules to prevent unnecessary execution.
    - Individual scripts must be explicitly imported as required.

Dependencies:
    - None (This module solely serves as an initialization file)

Example:
    ```python
    from scripts import example_script
    example_script.run()
    ```
"""

# Package version
__version__ = "0.1.0"
