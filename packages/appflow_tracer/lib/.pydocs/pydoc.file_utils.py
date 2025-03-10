#!/usr/bin/env python3

# Python File: ./packages/appflow_tracer/lib/file_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/appflow_tracer/lib/file_utils.py

Description:
    The file_utils.py module provides helper functions for managing log files,
    resolving relative paths, and cleaning terminal output by removing ANSI escape codes.

Core Features:
    - **Log File Management**: Removes old logs to prevent excessive storage usage.
    - **Project File Detection**: Verifies whether a file belongs to the project.
    - **Path Resolution**: Converts absolute paths into project-relative paths.
    - **ANSI Escape Code Removal**: Cleans formatted terminal output.
    - **Module Execution**: Supports a main entry point for potential extensions.

Usage:
    To clean up old log files:
        from file_utils import manage_logfiles
        manage_logfiles(configs=CONFIGS)

    To check if a file belongs to the project:
        from file_utils import is_project_file
        is_project_file("scripts/devops-workflow.py")

Dependencies:
    - sys - Handles system interactions.
    - re - Provides regex utilities for ANSI escape sequence removal.
    - pathlib - Handles file system operations.
    - lib.system_variables - Imports project-wide settings.
    - lib.log_utils - Logs file management operations.

Global Behavior:
    - Log files are removed only when exceeding the maximum allowed limit.
    - Project-relative paths exclude `.py` extensions for consistency.
    - ANSI escape codes are removed without altering message content.
    - The `main()` function serves as a placeholder for future extensions.

CLI Integration:
    This module is primarily used for internal utilities but can be executed directly.

Example Execution:
    ```python
    from file_utils import relative_path
    print(relative_path("/absolute/path/to/script.py"))
    ```

Expected Behavior:
    - Successfully manages log files without exceeding storage limits.
    - Converts absolute paths to project-relative paths when applicable.
    - Strips ANSI escape sequences while preserving readable content.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to file system or logging issues.
"""

FUNCTION_DOCSTRINGS = {
    "is_project_file": """
    Function: is_project_file(filename: str) -> bool
    Description:
        Determines if a given file path belongs to the project directory structure.

    Parameters:
        - filename (str): The absolute or relative file path to be checked.

    Returns:
        - bool: True if the file is within the project directory, False otherwise.

    Example:
        >>> is_project_file("appflow_tracer/tracing.py")
        True
        >>> is_project_file("/usr/lib/python3.8/external.py")
        False

    Behavior:
        - Resolves the absolute path before performing the check.
        - Returns False if the filename is None or an empty string.

    Error Handling:
        - Gracefully handles unexpected inputs such as None or invalid paths.
    """,
    "manage_logfiles": """
    Function: manage_logfiles(configs: dict = None) -> list
    Description:
        Manages log file storage by removing old logs if the number exceeds a configured limit.

    Parameters:
        - configs (dict, optional): Configuration dictionary specifying:
            - `"max_logfiles"`: Maximum number of log files to retain.
            Defaults to the global `max_logfiles` setting if missing.

    Returns:
        - list: A list of deleted log file paths.

    Workflow:
        1. Identifies log files in the configured directory.
        2. Sorts log files by modification time.
        3. Deletes excess log files if the count exceeds the threshold.
        4. Logs deletions using `log_utils.log_message()`.

    Notes:
        - Ensures logging operations respect `configs["logging"]["enable"]`.
        - If no logs exceed the threshold, returns an empty list.

    Error Handling:
        - Catches `OSError` if a file cannot be deleted.
        - Logs errors using `log_utils.log_message()`.
    """,
    "relative_path": """
    Function: relative_path(filepath: str) -> str
    Description:
        Converts an absolute file path into a project-relative path.

    Parameters:
        - filepath (str): The absolute file path to convert.

    Returns:
        - str: The relative path within the project, or the original path if it
          cannot be converted.

    Example:
        >>> relative_path("/path/to/project/module.py")
        "module"

    Behavior:
        - If the file is outside the project directory, returns the original path.
        - Removes the `.py` extension for consistency.

    Error Handling:
        - If the path is not within the project, returns the original file name.
    """,
    "remove_ansi_escape_codes": """
    Function: remove_ansi_escape_codes(text: str) -> str
    Description:
        Removes ANSI escape sequences from a string.

    Parameters:
        - text (str): The input string that may contain ANSI escape codes.

    Returns:
        - str: A new string with all ANSI escape codes removed.

    Example:
        >>> remove_ansi_escape_codes("\\x1b[31mThis is red text\\x1b[0m")
        "This is red text"

    Behavior:
        - Strips ANSI escape codes while preserving readable content.
        - Used for cleaning log messages or terminal output.

    Error Handling:
        - Ensures that formatted messages remain readable without altering text.
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
    "project_root": """
    - Description: Root directory of the project.
    - Type: Path
    - Usage: Used for resolving project-relative file paths.
    """,
    "project_logs": """
    - Description: Directory where log files are stored.
    - Type: Path
    - Usage: Ensures centralized logging across the project.
    """,
    "max_logfiles": """
    - Description: Maximum number of log files to retain per package.
    - Type: int
    - Usage: Enforces log retention policies to prevent excessive storage use.
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
}
