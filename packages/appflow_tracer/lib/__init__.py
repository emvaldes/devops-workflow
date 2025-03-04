#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/__init__.py
# Version: 0.1.0

"""
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

Submodules:
    - `file_utils`: Provides file and directory management utilities.
    - `log_utils`: Handles structured logging and message formatting.
    - `trace_utils`: Supports runtime tracing and performance monitoring.
    - `serialize_utils`: Manages data serialization and deserialization.

Usage:
    To import specific utilities from this package:
    ```python
    from packages.appflow_tracer.lib import log_utils, file_utils

    log_utils.log_message("Example log message")
    file_utils.manage_logfiles()
    ```

Dependencies:
    - None (This module only manages imports)

Example:
    ```python
    from packages.appflow_tracer.lib import trace_utils
    trace_utils.start_tracing()
    ```
"""

# Package version
__version__ = "0.1.0"

# Import and expose key submodules
from . import (
    file_utils,
    log_utils,
    trace_utils,
    serialize_utils,
    trace_utils
)

__all__ = [
    "file_utils",
    "log_utils",
    "trace_utils",
    "serialize_utils",
    "trace_utils"
]
