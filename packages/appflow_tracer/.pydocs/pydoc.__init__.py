#!/usr/bin/env python3

# Python File: ./packages/appflow_tracer/__init__.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: packages/appflow_tracer/__init__.py

Description:
    AppFlow Tracing Package Initialization

    This module serves as the entry point for the `appflow_tracer` package, ensuring
    the package is correctly recognized and exposing core functionalities for structured
    logging and function execution tracing.

Core Features:
    - **Package Initialization**: Marks `appflow_tracer` as a Python package, enabling imports.
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
    Importing and initializing logging:
        from packages.appflow_tracer import setup_logging
        CONFIGS = setup_logging()

    Logging messages:
        from packages.appflow_tracer import log_utils
        log_utils.log_message("This is a test log message.")

    Accessing tracing utilities:
        from packages.appflow_tracer import trace_utils
        trace_utils.start_tracing()

Dependencies:
    - `tracing` - Manages function execution tracing and structured event logging.
    - `log_utils` - Handles structured logging, formatting, and log management.
    - `file_utils` - Provides file and directory-related utilities.
    - `serialize_utils` - Ensures proper data serialization and deserialization.
    - `trace_utils` - Supports real-time function call monitoring and execution tracing.

Exit Codes:
    - `0`: Successful package initialization.
    - `1`: Failure due to import errors or incorrect setup.

Example:
    Initializing the AppFlow Tracer system:
        from packages.appflow_tracer import setup_logging, log_utils

        CONFIGS = setup_logging()
        log_utils.log_message("Framework initialized successfully.")
"""

FUNCTION_DOCSTRINGS = {
    "setup_logging": """
    Configures and initializes structured logging for the framework.

    This function sets up logging with file and console handlers, ensuring structured
    log output. It integrates function call tracing and manages log file retention.

    Args:
        configs (dict, optional): Logging configuration dictionary.
        logname_override (str, optional): Custom log file name.
        events (bool, list, dict, optional): Controls which events are logged.

    Returns:
        dict: The effective logging configuration.

    Example:
        >>> from packages.appflow_tracer import setup_logging
        >>> CONFIGS = setup_logging()
    """
}

VARIABLE_DOCSTRINGS = {
    "__all__": """
    - Description: Defines the public API of the `appflow_tracer` package.
    - Type: list
    - Contents:
        - "setup_logging": Initializes structured logging.
        - "file_utils": Provides file management utilities.
        - "log_utils": Handles structured logging.
        - "serialize_utils": Supports safe serialization.
        - "trace_utils": Implements function call tracing.
    """
}
