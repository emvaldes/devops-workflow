#!/usr/bin/env python3

# Python File: ./packages/appflow_tracer/lib/__init__.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: packages/appflow_tracer/lib/__init__.py

Description:
    AppFlow Tracer Library Initialization

    This file defines the `lib` subpackage within the `appflow_tracer` framework. It provides
    access to essential utility modules required for logging, file operations, tracing, and
    serialization within the framework.

Core Features:
    - **Subpackage Initialization**: Ensures that the `lib` directory is recognized as a Python package.
    - **Utility Module Exposure**: Facilitates direct access to key framework utilities.
    - **Structured Imports**: Enables clean and maintainable access to core functionality.
    - **Dynamic Documentation Loading**: Injects `.pydoc` documentation into the module.

Submodules:
    - `file_utils`: Provides file and directory management utilities.
    - `log_utils`: Handles structured logging and message formatting.
    - `trace_utils`: Supports runtime tracing and performance monitoring.
    - `serialize_utils`: Manages data serialization and deserialization.

Usage:
    To import specific utilities from this package:
        from packages.appflow_tracer.lib import log_utils, file_utils

        log_utils.log_message("Example log message")
        file_utils.manage_logfiles()

    To enable tracing within the framework:
        from packages.appflow_tracer.lib import trace_utils
        trace_utils.start_tracing()

Dependencies:
    - `sys` - Provides access to system path management.
    - `pathlib.Path` - Used for resolving package paths dynamically.
    - `lib.pydoc_loader` - Dynamically loads module-level documentation.

Example:
    Importing core utilities from the `appflow_tracer` library:
        from packages.appflow_tracer.lib import log_utils, serialize_utils

        log_utils.log_message("Structured logging enabled")
        json_data = serialize_utils.safe_serialize({"example": "data"})
"""

FUNCTION_DOCSTRINGS = {}

VARIABLE_DOCSTRINGS = {
    "__all__": """
    - Description: Specifies the public API for the `lib` package.
    - Type: list[str]
    - Usage: Defines the modules exposed when using `from lib import *`.

    Modules:
        - `file_utils`: Provides file and directory management utilities.
        - `log_utils`: Handles structured logging and message formatting.
        - `trace_utils`: Supports runtime tracing and performance monitoring.
        - `serialize_utils`: Manages data serialization and deserialization.
    """
}
