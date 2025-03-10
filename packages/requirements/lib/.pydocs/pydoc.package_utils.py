#!/usr/bin/env python3

# Python File: ./packages/requirements/lib/package_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/requirements/lib/package_utils.py

Description:
    The package_utils.py module provides structured functions for managing Python dependencies,
    supporting backup, restore, installation, and compliance enforcement based on predefined policies.

Core Features:
    - Backup & Restore Packages: Saves and restores installed packages for migration or disaster recovery.
    - Policy-Based Package Installation: Enforces version compliance through installation, upgrades, or downgrades.
    - Dependency Review & Management: Evaluates installed versions against required versions.
    - Homebrew & Pip Integration: Uses Homebrew when applicable or defaults to Pip for package installation.
    - Logging & Configuration Handling: Ensures structured logging and configuration retrieval.

Usage:
    Backing Up Installed Packages:
        from packages.requirements.lib.package_utils import backup_packages
        backup_packages("backup.txt", configs)

    Installing a Specific Package:
        from packages.requirements.lib.package_utils import install_package
        install_package("requests", "2.26.0", configs)

    Installing Dependencies Based on Policy:
        from packages.requirements.lib.package_utils import install_requirements
        install_requirements(configs)

Dependencies:
    - sys - Handles system-level functions such as process termination.
    - subprocess - Executes shell commands for package management.
    - shutil - Verifies presence of external utilities.
    - json - Handles structured dependency files.
    - importlib.metadata - Retrieves installed package versions.
    - functools.lru_cache - Caches function calls for efficiency.
    - pathlib - Ensures platform-independent file path resolution.
    - packages.appflow_tracer.lib.log_utils - Provides structured logging.

Expected Behavior:
    - Ensures all required packages are installed, upgraded, or downgraded as per defined policies.
    - Respects externally managed environments and provides manual installation instructions when necessary.
    - Logs all package operations for debugging and compliance tracking.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to missing configurations, package errors, or restricted environments.
"""

FUNCTION_DOCSTRINGS = {
    "backup_packages": """
    Function: backup_packages(file_path: str, configs: dict) -> None
    Description:
        Saves all installed Python packages to a file for backup or migration.

    Parameters:
        - file_path (str): The file where the installed package list is saved.
        - configs (dict): Configuration dictionary for logging.

    Returns:
        - None: Writes the package list to the specified file.

    Behavior:
        - Runs 'pip freeze' to capture all installed packages.
        - Saves the package list to the specified file.
        - Logs the operation success or failure.

    Error Handling:
        - Captures subprocess errors if the 'pip freeze' command fails.
    """,
    "install_package": """
    Function: install_package(package: str, version: Optional[str] = None, configs: dict = None) -> None
    Description:
        Installs or updates a package using Homebrew (if applicable) or Pip.

    Parameters:
        - package (str): The package name to install.
        - version (Optional[str]): The specific version to install (default: latest).
        - configs (dict): Configuration dictionary for logging and system constraints.

    Returns:
        - None: Executes the installation process.

    Behavior:
        - Detects Python's installation method (Brew or standalone).
        - Installs the package using Brew if available, otherwise uses Pip.
        - Uses '--break-system-packages' when necessary to override restrictions.

    Error Handling:
        - Logs an error if installation fails due to system constraints.
        - Provides manual installation instructions when Pip installation is restricted.
    """,
    "install_requirements": """
    Function: install_requirements(configs: dict, bypass: bool = False) -> None
    Description:
        Installs, upgrades, or downgrades dependencies based on policy rules.

    Parameters:
        - configs (dict): Configuration dictionary containing dependency requirements.
        - bypass (bool): If True, forces installation without policy evaluation.

    Returns:
        - None: Executes necessary package actions.

    Behavior:
        - Evaluates package policies for installation, upgrade, or downgrade.
        - Installs packages using Brew or Pip based on system constraints.
        - Logs installation steps and policy decisions.

    Error Handling:
        - Logs warnings for missing configurations or restricted environments.
    """,
    "installed_configfile": """
    Function: installed_configfile(configs: dict) -> Path
    Description:
        Retrieves the configured path to `installed.json`, which tracks installed package statuses.

    Parameters:
        - configs (dict): The configuration dictionary.

    Returns:
        - Path: The resolved path to `installed.json`.

    Error Handling:
        - Raises KeyError if the configuration is missing the expected path.
    """,
    "migrate_packages": """
    Function: migrate_packages(file_path: str, configs: dict) -> None
    Description:
        Migrates installed packages from a previous environment and saves the package list.

    Parameters:
        - file_path (str): File path to save the list of installed packages.
        - configs (dict): Configuration dictionary for logging.

    Returns:
        - None: Executes the migration process.

    Behavior:
        - Extracts installed packages using 'pip list'.
        - Saves package names before re-installing them.
        - Installs all packages in the new environment.

    Error Handling:
        - Logs errors if package retrieval or installation fails.
    """,
    "packages_installed": """
    Function: packages_installed(configs: dict) -> None
    Description:
        Prints the installed dependencies in a readable format.

    Parameters:
        - configs (dict): Configuration dictionary.

    Returns:
        - None: Displays installed packages and their status.

    Behavior:
        - Reads `installed.json` and logs package names and versions.
        - Checks compliance against required versions.

    Error Handling:
        - Logs an error if `installed.json` is missing or corrupted.
    """,
    "restore_packages": """
    Function: restore_packages(file_path: str, configs: dict) -> None
    Description:
        Restores previously backed-up Python packages from a saved package list.

    Parameters:
        - file_path (str): Path to the package list generated by `pip freeze`.
        - configs (dict): Configuration dictionary for logging.

    Returns:
        - None: Installs packages from the saved list.

    Behavior:
        - Reads the package list and installs them using Pip.
        - Ensures compatibility with existing package versions.

    Error Handling:
        - Logs errors if installation fails or if the backup file is missing.
    """,
    "review_packages": """
    Function: review_packages(configs: dict) -> list
    Description:
        Reviews installed package versions and returns a structured package status list.

    Parameters:
        - configs (dict): Configuration dictionary.

    Returns:
        - list: A list of reviewed package data including installation status.

    Behavior:
        - Compares installed versions against required versions.
        - Determines whether a package is installed, outdated, or missing.
        - Writes updated package statuses to `installed.json`.

    Error Handling:
        - Logs an error if version comparisons fail.
    """,
}

VARIABLE_DOCSTRINGS = {
    "LIB_DIR": """
    - Description: Defines the library directory path.
    - Type: Path
    - Usage: Dynamically added to sys.path for resolving imports.
    """,
    "environment": """
    - Description: Stores system-wide environment variables for dependency management.
    - Type: module
    - Usage: Provides access to configuration and logging utilities.
    """,
    "installed_filepath": """
    - Description: Stores the path to `installed.json`, tracking installed package statuses.
    - Type: Path
    - Usage: Used for backup, restore, and compliance enforcement.
    """,
}
