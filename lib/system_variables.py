#!/usr/bin/env python3

# File: ./lib/system_variables.py
__version__ = "0.1.0"  ## Package version

"""
File: ./lib/system_variables.py

Description:
    System-Wide Configuration Paths and Variables
    This module defines system-wide constants and configuration file paths
    that serve as references throughout the framework.

Core Features:
    - **Standardized Configuration Paths**: Defines paths for `.env`, `runtime-params.json`, etc.
    - **Project Root Management**: Establishes a unified reference for directory traversal.
    - **Dynamic Configuration Aggregation**: Aggregates available configuration files.
    - **Log File Quota Management**: Restricts the number of stored logs for efficiency.

Usage:
    Note: This module is imported wherever system-wide file path references are required.

    ```python
    from lib.system_variables import category, project_root
    log_utils.log_message("This is a test", category.info.id)
    ```

Dependencies:
    - pathlib (for filesystem path handling)
    - types.SimpleNamespace (for structured category labels)

Global Variables:
    - `project_root` (Path): Base directory for resolving project files.
    - `project_logs` (Path): Directory where log files are stored.
    - `project_packages` (Path): Path to the package directory.
    - `env_filepath` (Path): Location of the `.env` file for runtime parameters.
    - `runtime_params_filepath` (Path): Stores dynamically generated runtime parameters.
    - `system_params_filepath` (Path): Stores global system-wide configurations.
    - `project_params_filepath` (Path): Stores project-level configurations.
    - `default_params_filepath` (Path): Defines framework default parameters.
    - `system_params_listing` (List[Path]): Aggregates configuration sources dynamically.
    - `max_logfiles` (int): Restricts the number of stored logs (default: `5`).
    - `default_indent` (int): Default JSON indentation for formatting.

Structured Logging Categories:
    - `category` (SimpleNamespace): Predefined logging categories for structured logging.
        - `category.calls.id`    ("CALL"): Function calls.
        - `category.critical.id` ("CRITICAL"): Critical system failures.
        - `category.debug.id`    ("DEBUG"): Debugging messages.
        - `category.error.id`    ("ERROR"): Error messages.
        - `category.imports.id`  ("IMPORT"): Module imports.
        - `category.info.id`     ("INFO"): Informational messages.
        - `category.returns.id`  ("RETURN"): Function return values.
        - `category.warning.id`  ("WARNING"): Warnings.

    Purpose:
    - Provides a structured way to reference log categories using dot-notation.
    - Reduces hardcoded strings in logging calls for consistency.
    - Improves readability and maintainability of log messages.

Expected Behavior:
    - Configuration paths should always resolve correctly, ensuring consistency.
    - `max_logfiles` should ideally be configurable via an environment variable.
    - System parameter files should be aggregated dynamically for flexibility.

Example:
    ```python
    from lib.system_variables import project_root, system_params_filepath

    print(f"Project Root: {project_root}")
    print(f"System Params File: {system_params_filepath}")
    ```
"""

from types import SimpleNamespace as simple
from pathlib import Path

"""
The root directory of the project.
This is used to resolve paths for all configurations and logs dynamically.
"""
project_root = Path(__file__).resolve().parent.parent


"""
Directory path where all log files are stored.
Logs are structured under `logs/<package-name>/<module-name>-<timestamp>.log`.
"""
project_logs = project_root / "logs"

"""
Directory path where all Python packages (`packages/`) are stored.
"""
project_packages = project_root / "packages"

"""
Path to the `.env` file containing runtime environment variables.
Used by the `dotenv` package for loading environment configurations dynamically.
"""
env_filepath = project_root / ".env"

"""
Path to the `runtime-params.json` file.
This file is dynamically generated at runtime by merging system-wide (`default-params.json`)
and project-specific (`project-params.json`) parameters.
"""
runtime_params_filename = "runtime-params.json"
runtime_params_filepath = project_root / "configs" / runtime_params_filename

"""
Path to the `system-params.json` file.
This file stores global system-wide configurations.
"""
system_params_filename = "system-params.json"
system_params_filepath = project_root / "configs" / system_params_filename

"""
Path to the `project-params.json` file.
This file stores project-specific configurations, typically customized by the user.
"""
project_params_filename = "project-params.json"
project_params_filepath = project_root / "configs" / project_params_filename

"""
Path to the `default-params.json` file.
This file contains standardized, framework-wide default parameters.
"""
default_params_filename = "default-params.json"
default_params_filepath = project_root / "configs" / default_params_filename

"""
List of JSON configuration files used for system parameter aggregation.

Includes:
- `project-params.json`
- `default-params.json`
"""
system_params_listing = [
    project_params_filepath,
    default_params_filepath
]

"""
Maximum number of log files allowed per module.
If the number of logs exceeds this limit, older logs are pruned automatically.
Default: `5`
"""
max_logfiles = 5

"""
Default JSON indentation (formatting)
"""
default_indent = 4

"""
Predefined logging categories for structured logging.
"""
category = simple(
    calls    = simple(id="CALL",     color="\033[92m"),  # Green
    critical = simple(id="CRITICAL", color="\033[41m"),  # Red Background
    debug    = simple(id="DEBUG",    color="\033[96m"),  # Cyan
    error    = simple(id="ERROR",    color="\033[31m"),  # Bright Red
    imports  = simple(id="IMPORT",   color="\033[94m"),  # Blue
    info     = simple(id="INFO",     color="\033[97m"),  # White
    returns  = simple(id="RETURN",   color="\033[93m"),  # Yellow
    warning  = simple(id="WARNING",  color="\033[91m"),  # Red
    reset    = simple(id="RESET",    color="\033[0m")    # Reset to default
)
