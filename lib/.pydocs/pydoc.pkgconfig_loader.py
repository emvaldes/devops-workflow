#!/usr/bin/env python3

# Python File: ./lib/pkgconfig_loader.py
__version__ = "0.1.0"  # Documentation version

# Module-level documentation
MODULE_DOCSTRING = """
Overview:
    The pkgconfig_loader.py module is responsible for loading and managing package configuration files.
    It provides methods for parsing, validating, and retrieving configuration data from structured files (e.g., JSON).

Core Features:
    - Configuration File Loading: Reads and parses package configuration files.
    - Validation Support: Ensures required parameters are present.
    - Structured Access: Provides a structured interface for retrieving configuration values.
    - Logging and Debugging: Ensures consistent logging across packages.

Usage:
    Loading a package-specific configuration:
        from lib.pkgconfig_loader import package_configs
        config = package_configs()

    Setting up logging for a module:
        setup_configs("/path/to/module.py")

Dependencies:
    - os, sys, json, pathlib, datetime
    - system_variables: Provides project-wide settings and configurations.

Exit Codes:
    - 0: Successful execution.
    - 1: Failure due to missing or invalid configuration files.
"""

# Function-level documentation
FUNCTION_DOCSTRINGS = {
    "config_logfile": """
    Determines the correct log file path based on the caller module's request or self-inspection.

    Parameters:
        config (dict): Configuration dictionary containing logging settings.
        caller_log_path (Optional[str]): A specific log directory path requested by the caller.

    Returns:
        Path: The resolved log file path.
""",

    "package_configs": """
    Loads a package-specific configuration from a JSON file or generates a default configuration.

    Parameters:
        overrides (Optional[dict]): Configuration values to override defaults.

    Returns:
        dict: The loaded or generated package configuration.

    Raises:
        FileNotFoundError: If the configuration file is missing.
        json.JSONDecodeError: If the file contains invalid JSON.
""",

    "setup_configs": """
    Dynamically initializes and updates logging configuration for the calling module.

    Parameters:
        absolute_path (Path): The absolute path of the module requesting logging setup.
        logname_override (Optional[str]): A custom name for the log file.
        events (Optional[Union[bool, list, dict]]): Event control settings.

    Returns:
        dict: The updated logging configuration.
"""
}

VARIABLE_DOCSTRINGS = {
    "timestamp": "Unique timestamp string used for log filenames.",
    "project_root": "Root directory of the project, retrieved from system variables.",
    "project_logs": "Directory path for storing logs, retrieved from system variables.",
    "max_logfiles": "Maximum number of log files allowed before rotation.",
    "default_indent": "Default indentation level for JSON output formatting.",
    "category": "Dictionary containing log categories and their respective identifiers.",
}
