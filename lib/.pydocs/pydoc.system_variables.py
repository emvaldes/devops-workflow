#!/usr/bin/env python3

# Python File: ./lib/system_variables.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./lib/system_variables.py

Description:
    The system_variables.py module defines global paths, file names, and system-wide constants
    for managing configurations, logging, and runtime parameter storage.

Core Features:
    - **Project Path Management**: Defines and resolves key project directories.
    - **Configuration File Paths**: Stores paths to runtime, system, and default configuration files.
    - **Logging System Variables**: Defines log storage locations and log file retention settings.
    - **ANSI Color Categories**: Provides categorized ANSI escape codes for structured terminal output.
    - **Global Constants**: Stores universal defaults such as JSON indentation levels and max log files.

Usage:
    Importing System Variables:
        from lib.system_variables import project_root, project_logs
        print(f"Project logs are stored in: {project_logs}")

    Using ANSI Log Categories:
        from lib.system_variables import category
        print(f"{category.info.color}INFO: This is a test log{category.reset.color}")

Dependencies:
    - types.SimpleNamespace - Defines structured namespaces for category-based logging.
    - pathlib.Path - Ensures safe and platform-independent file path resolution.

Global Behavior:
    - Provides a centralized reference for all project-wide variables.
    - Ensures consistency across modules by defining static paths and configurations.
    - Enhances logging with structured color-coded categories.

CLI Integration:
    This module is designed as a global reference but can be imported for debugging system paths.

Example Execution:
    python system_variables.py

Expected Behavior:
    - Successfully defines all necessary global paths and system-wide constants.
    - Provides a structured way to manage logging, configuration, and runtime parameters.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Error encountered during variable initialization.
"""

FUNCTION_DOCSTRINGS = {}

VARIABLE_DOCSTRINGS = {
    "project_root": """
    - Description: Root directory of the project.
    - Type: Path
    - Usage: Used as the base directory for resolving relative paths.
    """,
    "project_logs": """
    - Description: Directory where log files are stored.
    - Type: Path
    - Usage: Ensures centralized logging across the project.
    """,
    "project_packages": """
    - Description: Directory where Python packages are stored within the project.
    - Type: Path
    - Usage: Provides structured access to internal package modules.
    """,
    "env_filepath": """
    - Description: Path to the environment configuration file.
    - Type: Path
    - Usage: Stores environment variable settings loaded by dotenv.
    """,
    "runtime_params_filename": """
    - Description: Name of the JSON file that stores runtime parameters.
    - Type: str
    - Usage: Used for dynamically managing runtime configurations.
    """,
    "runtime_params_filepath": """
    - Description: Full path to the runtime parameters JSON file.
    - Type: Path
    - Usage: Used for loading and storing runtime configuration settings.
    """,
    "system_params_filename": """
    - Description: Name of the JSON file that stores system-wide parameters.
    - Type: str
    - Usage: Stores global system settings for application behavior.
    """,
    "system_params_filepath": """
    - Description: Full path to the system parameters JSON file.
    - Type: Path
    - Usage: Used for loading persistent system configuration settings.
    """,
    "project_params_filename": """
    - Description: Name of the JSON file that stores project-specific parameters.
    - Type: str
    - Usage: Stores project-related configuration settings.
    """,
    "project_params_filepath": """
    - Description: Full path to the project parameters JSON file.
    - Type: Path
    - Usage: Used to manage project-specific configuration settings.
    """,
    "default_params_filename": """
    - Description: Name of the JSON file that stores default parameters.
    - Type: str
    - Usage: Provides fallback values for missing configurations.
    """,
    "default_params_filepath": """
    - Description: Full path to the default parameters JSON file.
    - Type: Path
    - Usage: Ensures availability of base-level configurations.
    """,
    "system_params_listing": """
    - Description: List of system parameter files used for configuration merging.
    - Type: list[Path]
    - Usage: Used to merge multiple configuration sources dynamically.
    """,
    "max_logfiles": """
    - Description: Maximum number of log files to retain per package.
    - Type: int
    - Usage: Enforces log retention policies to prevent excessive storage use.
    """,
    "default_indent": """
    - Description: Default indentation level for JSON output.
    - Type: int
    - Usage: Ensures consistent formatting across configuration files.
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
