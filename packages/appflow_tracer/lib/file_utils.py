#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/file_utils.py
__version__ = "0.1.0"  ## Package version

"""
File: packages/appflow_tracer/lib/file_utils.py

Description:
    File and Log Management Utilities
    This module provides helper functions for managing log files, resolving
    relative paths, and cleaning terminal output by removing ANSI escape codes.

Core Features:
    - **Log File Management**: Removes old logs to prevent excessive storage usage.
    - **Project File Detection**: Verifies whether a file belongs to the project.
    - **Path Resolution**: Converts absolute paths into project-relative paths.
    - **ANSI Escape Code Removal**: Cleans formatted terminal output.

Usage:
    To clean up old log files:
    ```python
    manage_logfiles(configs=CONFIGS)
    ```

    To check if a file belongs to the project:
    ```python
    is_project_file("scripts/devops-workflow.py")
    ```

Dependencies:
    - sys
    - re
    - pathlib
    - lib.system_variables (for project settings)

Global Variables:
    - Uses `project_root`, `project_logs`, and `category` from `lib.system_variables`.

Expected Behavior:
    - Log files are removed only when exceeding the maximum allowed limit.
    - Project-relative paths exclude `.py` extensions for consistency.
    - ANSI escape codes are removed without altering message content.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to file system or logging issues.

Example:
    ```python
    from file_utils import relative_path
    print(relative_path("/absolute/path/to/script.py"))
    ```
"""

import sys
import re

from pathlib import Path

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs,
    max_logfiles,
    default_indent,
    category
)

from . import (
    log_utils
)

def is_project_file(
    filename: str
) -> bool:
    """
    Determine if a given file path belongs to the project directory structure.

    This function verifies whether the specified `filename` is located within
    the project's root directory and is not an external dependency.

    Args:
        filename (str): The absolute or relative file path to be checked.

    Returns:
        bool: True if the file is within the project directory, False otherwise.

    Example:
        >>> is_project_file("appflow_tracer/tracing.py")
        True
        >>> is_project_file("/usr/lib/python3.8/external.py")
        False

    Notes:
        - If the filename is `None` or an empty string, the function returns `False`.
        - The function safely resolves the absolute path before performing the check.
    """

    if not filename:
        # log_utils.log_message("is_project_file received None or empty filename.", category.info.id)
        return False
    try:
        filename_path = Path(filename).resolve()
        # log_utils.log_message("Resolved filename_path: {filename_path}", category.info.id)
        return project_root in filename_path.parents
    except (TypeError, ValueError):
        # Handle None or unexpected inputs gracefully
        return False

def manage_logfiles(
    configs: dict = None
) -> list:
    """
    Manage log file storage by removing old logs if the number exceeds a configured limit.

    This function prevents log directories from growing indefinitely by:
    - Checking the current number of log files in each log subdirectory.
    - Deleting the oldest logs **only if** the total count exceeds the allowed limit.

    Args:
        configs (dict, optional): Configuration dictionary that specifies:
            - `"max_logfiles"`: Maximum number of log files to retain.
            Defaults to `None`, in which case the global `max_logfiles` setting is used.

    Raises:
        OSError: If an error occurs while attempting to delete log files.

    Returns:
        list: A list of deleted log file paths.

    Workflow:
        1. Sorts log files by modification time (oldest first).
        2. Identifies files exceeding the limit.
        3. Deletes excess log files.
        4. Logs deletions using `log_utils.log_message()`.

    Notes:
        - The function ensures logging operations respect the `configs["logging"]["enable"]` flag.
        - If no logs exceed the threshold, no deletions occur, and an empty list is returned.
    """

    logs_dir = Path(configs["logging"]["logs_dirname"])  # Target the correct logs directory
    deleted_logs = []
    if not logs_dir.exists() or not logs_dir.is_dir():
        return deleted_logs  # If the log directory doesn't exist, return empty
    log_files = sorted(
        logs_dir.glob("*.log"),  # Only target logs in the configured directory
        key=lambda f: f.stat().st_mtime  # Sort by modification time (oldest first)
    )
    num_to_remove = len(log_files) - configs["logging"].get("max_logfiles", 5)  # Default max to 5 if missing
    if num_to_remove > 0:
        logs_to_remove = log_files[:num_to_remove]  # Get oldest logs to remove
        for log_file in logs_to_remove:
            try:
                log_file.unlink()  # Delete the log file
                deleted_logs.append(log_file.as_posix())
                # Ensure logging only runs if enabled
                if configs["logging"].get("enable", True):
                    log_utils.log_message(f'Deleted old log: {log_file.as_posix()}', category.warning.id, configs=configs)
            except Exception as e:
                if configs["logging"].get("enable", True):
                    log_utils.log_message(f'Error deleting {log_file.as_posix()}: {e}', category.error.id, configs=configs)
    return deleted_logs

def relative_path(
    filepath: str
) -> str:
    """
    Convert an absolute file path into a project-relative path.

    This function maps the given absolute path to the project’s directory structure.
    If the file is outside the project, it returns the original path as a fallback.
    The `.py` extension is removed from the resulting path for consistency.

    Args:
        filepath (str): The absolute file path to convert.

    Returns:
        str: The relative path within the project, or the original path if it
        cannot be converted.

    Example:
        >>> relative_path("/path/to/project/module.py")
        "module"

    Notes:
        - If the file is not within the project directory, the original path is returned.
        - The `.py` extension is removed for consistency in logging and output formatting.
    """

    try:
        return str(Path(filepath).resolve().relative_to(project_root)).replace(".py", "")
    except ValueError:
        return filepath.replace(".py", "")  # Return original if not within project

def remove_ansi_escape_codes(
    text: str
) -> str:
    """
    Remove ANSI escape sequences from a string.

    This function is used to clean up log messages or terminal output by
    stripping out escape codes that produce colored or formatted text.
    The resulting string contains only plain text.

    Args:
        text (str): The input string that may contain ANSI escape codes.

    Returns:
        str: A new string with all ANSI escape codes removed.

    Example:
        >>> remove_ansi_escape_codes("\x1b[31mThis is red text\x1b[0m")
        "This is red text"

    Notes:
        - ANSI escape codes are commonly used for terminal colorization.
        - The function ensures that formatted messages remain readable.
    """

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
