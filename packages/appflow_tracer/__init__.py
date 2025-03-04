#!/usr/bin/env python3

# File: ./packages/appflow_tracer/__init__.py
# Version: 0.1.0

"""
File Path: packages/appflow_tracer/__init__.py

Description:
    AppFlow Tracing Package Initialization

    This file defines the `appflow_tracer` package and ensures it is properly recognized
    as a Python package. It serves as the main entry point for tracing and logging functionalities
    by exposing the core `setup_logging` function along with key utilities.

Core Features:
    - **Package Initialization**: Marks `appflow_tracer` as a valid Python package.
    - **Logging Setup**: Provides `setup_logging` for configuring structured logging.
    - **Utility Exposure**: Imports and exposes core framework utilities for tracing, file handling, and logging.
    - **Modular Structure**: Ensures clean and organized access to tracing functionalities.

Submodules:
    - `tracing`: Handles structured event-based logging and tracing.
    - `lib.file_utils`: Provides file and directory management utilities.
    - `lib.log_utils`: Facilitates structured logging and debugging.
    - `lib.trace_utils`: Supports runtime tracing and performance monitoring.
    - `lib.serialize_utils`: Manages data serialization and deserialization.

Usage:
    To initialize logging within the framework:
    ```python
    from packages.appflow_tracer import setup_logging
    CONFIGS = setup_logging()
    ```

    To log messages:
    ```python
    from packages.appflow_tracer import log_utils
    log_utils.log_message("This is a test log message.")
    ```

Dependencies:
    - tracing (for structured event tracing)
    - log_utils (for logging and debugging)
    - file_utils (for file operations)
    - serialize_utils (for serialization handling)

Example:
    ```python
    from packages.appflow_tracer import setup_logging, log_utils

    CONFIGS = setup_logging()
    log_utils.log_message("Framework initialized successfully.")
    ```
"""

# Package version
__version__ = "0.1.0"

# from .tracing import (
from packages.appflow_tracer.tracing import (
    setup_logging
)

# from .lib import (
from packages.appflow_tracer.lib import (
    file_utils,
    log_utils,
    serialize_utils,
    trace_utils
)

# Explicitly define available functions
__all__ = [
    "setup_logging",
    "file_utils",
    "log_utils",
    "serialize_utils",
    "trace_utils"
]
