#!/usr/bin/env python3

# Python File: ./packages/requirements/lib/brew_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/requirements/lib/brew_utils.py

Description:
    The brew_utils.py module provides utility functions for integrating Homebrew
    package management within the dependency management system. It allows detection
    of Homebrew availability, identification of Python installation methods, and
    retrieval of installed and latest package versions.

Core Features:
    - Homebrew Availability Check: Determines whether Homebrew is installed.
    - Python Environment Detection: Identifies if Python is installed via Brew, system package managers, or standalone.
    - Package Version Retrieval: Fetches installed and latest versions of Homebrew-managed packages.

Usage:
    Checking Homebrew Availability:
        from packages.requirements.lib.brew_utils import check_availability
        is_brew_installed = check_availability()

    Detecting Python Installation Method:
        from packages.requirements.lib.brew_utils import detect_environment
        env_info = detect_environment()

    Fetching Homebrew Package Version:
        from packages.requirements.lib.brew_utils import brew_info
        version = brew_info("python3")

Dependencies:
    - sys - Handles system-level functions such as process termination.
    - subprocess - Runs Homebrew commands and captures output.
    - shutil - Checks if the `brew` command is available.
    - re - Provides regex-based parsing of command output.
    - json - Handles structured package information.
    - argparse - Parses command-line arguments.
    - platform - Identifies the operating system.
    - logging - Logs system events and errors.
    - importlib.metadata - Retrieves installed package versions.
    - functools.lru_cache - Optimizes function calls by caching results.
    - pathlib - Ensures safe and platform-independent file path resolution.

Expected Behavior:
    - Accurately detects the presence and operational status of Homebrew.
    - Determines Python installation method (Brew, system-managed, standalone).
    - Retrieves package version details from Homebrew.
    - Provides optimized querying with caching.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Error encountered in environment detection or package retrieval.
"""

FUNCTION_DOCSTRINGS = {
    "check_availability": """
    Function: check_availability() -> bool
    Description:
        Checks if Homebrew is installed and operational on macOS.

    Returns:
        - bool:
          - True if Homebrew is installed and functional.
          - False if Homebrew is unavailable or the system is not macOS.

    Behavior:
        - Uses shutil.which() to detect the Brew binary.
        - Runs 'brew --version' to verify Brew functionality.
        - Uses an LRU cache to avoid redundant system calls.

    Error Handling:
        - If Homebrew is missing, the function returns False.
    """,
    "brew_info": """
    Function: brew_info(package: str) -> Optional[str]
    Description:
        Queries Homebrew to determine if a package exists and fetches its version.

    Parameters:
        - package (str): The name of the package to check.

    Returns:
        - Optional[str]: The installed version of the package if found, otherwise None.

    Behavior:
        - Runs 'brew info <package>' and extracts the version from output.
        - If the package does not exist, returns None.

    Error Handling:
        - If Homebrew fails to retrieve package info, the function returns None.
    """,
    "detect_environment": """
    Function: detect_environment() -> dict
    Description:
        Detects the Python installation method and determines whether package installations are restricted.

    Returns:
        - dict: A dictionary containing:
          - "OS" (str): The detected operating system ("darwin", "linux", "windows").
          - "INSTALL_METHOD" (str): How Python is installed ("brew", "system", "standalone", "microsoft_store").
          - "EXTERNALLY_MANAGED" (bool): Whether the system restricts package installations.
          - "BREW_AVAILABLE" (bool): Whether Homebrew is installed.

    Behavior:
        - Detects if Python was installed via Brew.
        - Checks for EXTERNALLY-MANAGED markers on Linux/macOS.
        - Determines if Python is managed by APT/DNF on Linux or Microsoft Store on Windows.

    Error Handling:
        - Uses subprocess calls to query system information.
        - Returns a structured dictionary even if detection fails.
    """,
    "version": """
    Function: version(package: str) -> Optional[str]
    Description:
        Retrieves the installed version of a Homebrew-managed package.

    Parameters:
        - package (str): The name of the package to check.

    Returns:
        - Optional[str]: The installed version of the package if found, otherwise None.

    Behavior:
        - Runs 'brew list --versions <package>' and extracts the installed version.
        - Returns None if the package is not installed via Homebrew.

    Error Handling:
        - If Homebrew fails or the package is missing, the function returns None.
    """,
    "latest_version": """
    Function: latest_version(package: str) -> Optional[str]
    Description:
        Retrieves the latest available version of a Homebrew package.

    Parameters:
        - package (str): The name of the package to check.

    Returns:
        - Optional[str]: The latest available version from Homebrew, otherwise None.

    Behavior:
        - Runs 'brew info <package>' and extracts the stable version.
        - Uses regex to parse the latest version from Homebrew output.

    Error Handling:
        - If Brew command fails or package is missing, returns None.
    """,
}

VARIABLE_DOCSTRINGS = {
    "LIB_DIR": """
    - Description: Defines the library directory path.
    - Type: Path
    - Usage: Dynamically added to sys.path for resolving imports.
    """,
    "environment": """
    - Description: Stores system-wide environment variables for the dependency management system.
    - Type: module
    - Usage: Provides access to configuration and logging utilities.
    """,
}
