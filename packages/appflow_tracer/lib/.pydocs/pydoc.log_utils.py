#!/usr/bin/env python3

# Python File: ./packages/appflow_tracer/lib/log_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/appflow_tracer/lib/log_utils.py

Description:
    The log_utils.py module provides structured logging utilities for handling
    console and file-based logging. It ensures formatted, categorized logs with
    support for custom levels, structured data, and ANSI-colored output.

Core Features:
    - **Structured Log Messages**: Formats logs in a consistent manner.
    - **Console and File Logging**: Sends logs to both the console and log files.
    - **Custom Log Levels**: Supports INFO, WARNING, ERROR, DEBUG, etc.
    - **ANSI Color Support**: Enables colored output for terminal logs.
    - **JSON Data Logging**: Logs structured JSON data when required.

Usage:
    To log a structured message:
        from log_utils import log_message
        log_message("System initialized", category.info.id, json_data={"status": "ready"})

    To log a warning message:
        log_message("Configuration file missing", category.warning.id)

Dependencies:
    - sys - Handles system interactions.
    - json - Enables structured JSON-based logging.
    - logging - Provides core logging functionalities.
    - datetime - Manages log timestamps.
    - lib.system_variables - Loads global configuration settings.

Global Behavior:
    - Logs messages to both console and files based on configuration settings.
    - Maps log categories to appropriate logging levels (INFO, DEBUG, ERROR, etc.).
    - Ensures JSON data is formatted properly if included in log messages.
    - Supports disabling console logs while retaining file-based logs.

CLI Integration:
    This module primarily serves as an internal utility but can be extended.

Example Execution:
    ```python
    from log_utils import log_message
    log_message("Initialization complete", category.info.id)
    ```

Expected Behavior:
    - Ensures that logging configurations determine output destinations.
    - Formats log messages consistently with timestamps and levels.
    - Applies ANSI color formatting to enhance log visibility in terminals.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to logging configuration issues.
"""

FUNCTION_DOCSTRINGS = {
    "log_message": """
    Function: log_message(
        message: str,
        log_category: str = "INFO",
        json_data: dict = None,
        serialize_json: bool = False,
        configs: dict = None,
        handler: logging.Logger = None
    ) -> None
    Description:
        Logs a structured message with optional JSON data to both console and log files.

    Parameters:
        - message (str): The main log message.
        - log_category (str, optional): The log level/category (e.g., category.info.id, category.warning.id).
        - json_data (dict, optional): Additional structured JSON data to log.
        - serialize_json (bool, optional): If True, serializes `json_data` into a JSON string.
        - configs (dict, optional): Configuration dictionary. Defaults to global `CONFIGS` if not provided.
        - handler (logging.Logger, optional): The specific logger instance to use.

    Raises:
        - KeyError: If the provided log category is invalid.
        - TypeError: If `json_data` is not a dictionary when `serialize_json` is True.

    Returns:
        - None

    Workflow:
        1. Determines the correct log level based on `log_category`.
        2. Serializes JSON data if `serialize_json` is enabled.
        3. Logs the message to a file if file logging is enabled.
        4. Displays the message in the console if tracing is enabled.

    Example:
        >>> log_message("System initialized", category.info.id)
        >>> log_message("Missing config", category.warning.id)
        >>> log_message("Debug details", json_data={"module": "log_utils"})
    """,
    "output_logfile": """
    Function: output_logfile(
        logger: logging.Logger,
        message: str,
        log_category: str = "INFO",
        json_data: dict = None
    ) -> None
    Description:
        Writes a structured log message to a designated log file.

    Parameters:
        - logger (logging.Logger): The logger instance used for writing logs.
        - message (str): The log message text.
        - log_category (str, optional): The log level/category (defaults to "INFO").
        - json_data (dict, optional): Additional structured JSON data for the log entry.

    Raises:
        - OSError: If the log file cannot be accessed or written to.

    Returns:
        - None

    Workflow:
        1. Formats the log message with category and timestamp.
        2. Appends structured JSON data if provided.
        3. Writes the log entry to the designated log file.

    Example:
        >>> logger = logging.getLogger("app_logger")
        >>> output_logfile(logger, "This is a log message", category.debug.id)
    """,
    "output_console": """
    Function: output_console(
        message: str,
        log_category: str,
        json_data: dict = None,
        configs: dict = None
    ) -> None
    Description:
        Displays a structured log message in the console with optional ANSI color formatting.

    Parameters:
        - message (str): The main message to display.
        - log_category (str): The logging category (e.g., category.info.id, category.error.id).
        - json_data (dict, optional): Additional structured JSON data for output.
        - configs (dict, optional): Configuration dictionary for colors and formatting.

    Raises:
        - KeyError: If an invalid log category is provided.
        - TypeError: If `json_data` is not a dictionary.

    Returns:
        - None

    Workflow:
        1. Determines the ANSI color for the log category.
        2. Formats the message with ANSI color codes.
        3. Prints the formatted message to the console.
        4. Displays structured JSON data if provided.

    Example:
        >>> output_console("Service started", category.info.id)
        >>> output_console("Config warning", category.warning.id, {"path": "/etc/config"})
    """,
    "main": """
    Function: main() -> None
    Description:
        Main entry point for the module.

    Returns:
        - None: The function does not perform any operations.

    Behavior:
        - Serves as a placeholder for future extensions.
        - Ensures the module can be executed as a standalone script.

    Error Handling:
        - None required as the function is currently a placeholder.
    """,
}

VARIABLE_DOCSTRINGS = {
    "default_indent": """
    - Description: Defines the default indentation level for JSON output formatting.
    - Type: int
    - Usage: Used in JSON dumps to maintain structured formatting.
    """,
    "category": """
    - Description: Namespace containing ANSI color codes for categorized logging.
    - Type: SimpleNamespace
    - Usage: Used in logging functions to color-code output messages.

    Categories:
        - `calls` (Green): Logs function calls.
        - `critical` (Red Background): Indicates critical errors.
        - `debug` (Cyan): Logs debugging messages.
        - `error` (Bright Red): Indicates errors.
        - `imports` (Blue): Logs module imports.
        - `info` (White): Logs informational messages.
        - `returns` (Yellow): Logs function return values.
        - `warning` (Red): Logs warning messages.
        - `reset` (Default): Resets terminal color formatting.
    """,
    "log_levels": """
    - Description: Maps log categories to their respective logging levels.
    - Type: dict[str, int]
    - Usage: Used in `log_message()` to determine the correct log level dynamically.

    Example Mapping:
        - `category.calls.id` → `logging.INFO`
        - `category.returns.id` → `logging.DEBUG`
        - `category.warning.id` → `logging.WARNING`
        - `category.error.id` → `logging.ERROR`
        - `category.critical.id` → `logging.CRITICAL`
    """,
}
