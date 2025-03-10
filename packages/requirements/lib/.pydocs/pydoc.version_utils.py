#!/usr/bin/env python3

# Python File: ./packages/requirements/lib/version_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/requirements/lib/version_utils.py

Description:
    The version_utils.py module provides structured utilities for retrieving and managing package versions.
    It supports multi-platform package detection across Pip, Homebrew, APT, DNF, and Windows Package Manager.

Core Features:
    - Retrieve Installed Package Versions: Determines the currently installed version of a package.
    - Check Latest Available Versions: Queries the latest available package versions from the appropriate source.
    - Multi-Platform Support: Detects package versions across macOS (Homebrew), Linux (APT/DNF), and Windows (Microsoft Store).
    - Optimized Performance: Uses caching and structured queries to minimize redundant operations.
    - Logging & Debugging: Provides detailed debug logs for package evaluations.

Usage:
    Checking Installed Version:
        from packages.requirements.lib.version_utils import installed_version
        current_version = installed_version("requests", configs)

    Fetching Latest Available Version:
        from packages.requirements.lib.version_utils import latest_version
        latest_pip_version = latest_version("requests", configs)

Dependencies:
    - sys - Handles system-level functions such as process termination.
    - subprocess - Executes shell commands for package management.
    - json - Handles structured dependency files.
    - importlib.metadata - Retrieves installed package versions.
    - functools.lru_cache - Caches function calls for efficiency.
    - pathlib - Ensures platform-independent file path resolution.
    - packages.appflow_tracer.lib.log_utils - Provides structured logging.
    - brew_utils - Retrieves Homebrew-specific package versions.

Expected Behavior:
    - Ensures all required packages follow version compliance checks.
    - Prevents unintended upgrades/downgrades when policy is set to "restricted".
    - Logs all package version evaluations for debugging and compliance tracking.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to missing configurations, package errors, or policy conflicts.
"""

FUNCTION_DOCSTRINGS = {
    "latest_version": """
    Function: latest_version(package: str, configs: dict) -> Optional[str]
    Description:
        Fetches the latest available version of a package using the appropriate package manager.

    Parameters:
        - package (str): The package name to check.
        - configs (dict): Configuration dictionary used for logging and environment detection.

    Returns:
        - Optional[str]: The latest available version as a string if found, otherwise None.

    Behavior:
        - Prioritizes Pip for Python packages.
        - Uses system-level package managers (Homebrew, APT/DNF, Microsoft Store) as applicable.
    """,

    "installed_version": """
    Function: installed_version(package: str, configs: dict) -> Optional[str]
    Description:
        Retrieves the installed version of a package.

    Parameters:
        - package (str): The package name to check.
        - configs (dict): Configuration dictionary containing system environment details.

    Returns:
        - Optional[str]: The installed package version if found, otherwise None.

    Behavior:
        - Uses multiple detection methods, prioritizing Pip before system-level package managers.
        - Logs version evaluation details for debugging.
    """,

    "pip_latest_version": """
    Function: pip_latest_version(package: str) -> Optional[str]
    Description:
        Retrieves the latest available version of a package via Pip.

    Parameters:
        - package (str): The package name to check.

    Returns:
        - Optional[str]: The latest available version as a string if found, otherwise None.

    Behavior:
        - Uses `pip index versions <package>` to retrieve the latest available version.
        - Requires internet access to fetch version information from PyPI.
    """,

    "linux_version": """
    Function: linux_version(package: str) -> Optional[str]
    Description:
        Retrieves the installed version of a package via APT (Debian-based) or DNF (Fedora).

    Parameters:
        - package (str): The package name to check.

    Returns:
        - Optional[str]: The installed version if found, otherwise None.

    Behavior:
        - Uses `dpkg -s <package>` for APT and `rpm -q <package>` for DNF.
        - Ensures compatibility with Linux-based package managers.
    """,

    "linux_latest_version": """
    Function: linux_latest_version(package: str) -> Optional[str]
    Description:
        Retrieves the latest available version of a package via APT or DNF.

    Parameters:
        - package (str): The package name to check.

    Returns:
        - Optional[str]: The latest available version if found, otherwise None.

    Behavior:
        - Uses `apt-cache madison <package>` for APT and `dnf list available <package>` for DNF.
        - Ensures compatibility with system package management tools.
    """,

    "windows_version": """
    Function: windows_version(package: str) -> Optional[str]
    Description:
        Retrieves the installed version of a package via Microsoft Store.

    Parameters:
        - package (str): The package name to check.

    Returns:
        - Optional[str]: The installed version if found, otherwise None.

    Behavior:
        - Uses PowerShell `Get-AppxPackage` to check installed package versions.
        - Requires administrator privileges for execution.
    """,

    "windows_latest_version": """
    Function: windows_latest_version(package: str) -> Optional[str]
    Description:
        Retrieves the latest available version of a package via Microsoft Store.

    Parameters:
        - package (str): The package name to check.

    Returns:
        - Optional[str]: The latest available version if found, otherwise None.

    Behavior:
        - Uses PowerShell `Find-Package` to query available package versions.
        - Requires administrator privileges for execution.
    """,
}
