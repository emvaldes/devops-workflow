#!/usr/bin/env python3

# File: ./packages/requirements/lib/version_utils.py
# Version: 0.1.0

"""
# Version Management Utilities for Dependency Handling

## Overview
    This module provides utilities for retrieving and managing package versions across
    various package managers. It supports version detection for Python packages installed
    via Pip, Homebrew, APT, DNF, and Windows Package Manager (Microsoft Store).

## Features
    - **Retrieve Installed Package Versions:** Determines the currently installed version of a package.
    - **Check Latest Available Versions:** Queries the latest available package versions from the appropriate source.
    - **Multi-Platform Support:** Detects package versions across macOS (Homebrew), Linux (APT/DNF), and Windows (Microsoft Store).
    - **Optimized Performance:** Uses caching and structured queries to minimize redundant operations.
    - **Logging & Debugging:** Provides detailed debug logs for package evaluations.

## Usage
    This module is used internally by the dependency management system to dynamically
    assess package versions before applying installation policies.

## Dependencies
    - `subprocess`: For executing package manager commands.
    - `json`: For parsing structured package data.
    - `importlib.metadata`: For retrieving installed Python package versions.
    - `pathlib`: For managing system paths.
    - `log_utils`: Custom logging module for structured output.
    - `brew_utils`: Handles Homebrew-specific package version retrieval.

## Notes
    - This module prioritizes Pip-based queries before falling back to system-level package managers.
    - It ensures **structured decision-making** when evaluating package versions.
"""

import sys
import subprocess
import shutil

import json
import argparse
import platform
import logging

import importlib.metadata

from functools import lru_cache

from datetime import datetime, timezone
from typing import Optional, Union

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

from . import brew_utils

# ------------------------------------------------------

def latest_version(package: str, configs: dict) -> Optional[str]:
    """
    Fetch the latest available version of a package using the appropriate package manager.

    This function determines the latest available version of a package by querying:
        1. **Pip** (default for Python packages).
        2. **Homebrew** (if Python is managed via Brew on macOS).
        3. **APT/DNF** (if applicable on Linux).
        4. **Windows Package Manager** (Microsoft Store).

    ## Args:
        - `package` (`str`): The package name to check.
        - `configs` (`dict`): Configuration dictionary used for logging and environment detection.

    ## Returns:
        - `Optional[str]`: The latest available version as a string if found, otherwise `None`.

    ## Notes:
        - Prioritizes Pip as it provides the most up-to-date package information.
        - Uses `match` statements to route requests to the correct package manager.
    """

    env_info = configs.get("environment", {})
    install_method = env_info.get("INSTALL_METHOD")

    # Default: Always check Pip first
    latest_pip_version = pip_latest_version(package)
    if latest_pip_version:
        return latest_pip_version  # Return immediately if Pip has it

    # Dispatch to correct package manager
    match install_method:
        case "brew":
            return brew_utils.latest_version(package)
        case "system":
            return linux_latest_version(package)
        case "microsoft_store":
            return windows_latest_version(package)

    return None  # No version found

## -----------------------------------------------------------------------------

def linux_version(package: str) -> Optional[str]:
    """
    Retrieve the installed version of a package via APT (Debian-based) or DNF (Fedora).

    This function attempts to determine the installed version using:
        - `dpkg -s <package>` for APT (Debian-based systems).
        - `rpm -q <package>` for DNF (Fedora-based systems).

    ## Args:
        - `package` (`str`): The package name to check.

    ## Returns:
        - `Optional[str]`: The installed version if found, otherwise `None`.

    ## Notes:
        - If `dpkg` is unavailable, it falls back to `rpm`.
    """

    try:
        result = subprocess.run(
            [ "dpkg", "-s", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass  # DPKG not found or package missing, try RPM

    try:
        result = subprocess.run(
            [ "rpm", "-q", package ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None  # RPM also not found or package missing

## -----------------------------------------------------------------------------

def linux_latest_version(package: str) -> Optional[str]:
    """
    Retrieve the latest available version of a package via APT or DNF.

    This function checks:
        - `apt-cache madison <package>` for APT (Debian-based systems).
        - `dnf list available <package>` for DNF (Fedora-based systems).

    ## Args:
        - `package` (`str`): The package name to check.

    ## Returns:
        - `Optional[str]`: The latest available version if found, otherwise `None`.

    ## Notes:
        - If `apt-cache` is unavailable, it falls back to `dnf`.
    """

    try:
        result = subprocess.run(
            [ "apt-cache", "madison", package ],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            return result.stdout.splitlines()[0].split("|")[1].strip()  # Extract version
    except FileNotFoundError:
        pass  # Try DNF if APT is unavailable

    try:
        result = subprocess.run(
            [ "dnf", "list", "available", package ],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            return result.stdout.splitlines()[1].split()[1]  # Extract version
    except FileNotFoundError:
        return None  # No package manager found

# ------------------------------------------------------

def windows_version(package: str) -> Optional[str]:
    """
    Retrieve the installed version of a package via Microsoft Store.

    This function runs a PowerShell command to check the installed version of
    a package using `Get-AppxPackage`.

    ## Args:
        - `package` (`str`): The package name to check.

    ## Returns:
        - `Optional[str]`: The installed version if found, otherwise `None`.

    ## Notes:
        - Uses PowerShell commands, which require administrator privileges.
    """

    try:
        result = subprocess.run(
            [ "powershell", "-Command", f'(Get-AppxPackage -Name {package}).Version' ],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        return version if version else None  # ✅ Return None if no output is found
    except subprocess.CalledProcessError:
        return None  # ✅ If the command fails, the package is missing

## -----------------------------------------------------------------------------

def windows_latest_version(package: str) -> Optional[str]:
    """
    Retrieve the latest available version of a package via Microsoft Store.

    This function runs a PowerShell command to check the latest available version
    of a package using `Find-Package`.

    ## Args:
        - `package` (`str`): The package name to check.

    ## Returns:
        - `Optional[str]`: The latest available version if found, otherwise `None`.

    ## Notes:
        - Requires PowerShell execution privileges.
    """

    try:
        result = subprocess.run(
            [ "powershell", "-Command", f'(Find-Package -Name {package}).Version' ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.stdout else None
    except subprocess.CalledProcessError:
        return None  # Package not found

## -----------------------------------------------------------------------------

def installed_version(package: str, configs: dict) -> Optional[str]:
    """
    Retrieve the installed version of a package.

    This function checks for an installed package version using the following priority order:
        1. **Pip (`pip list --format=json`)** - Best for detecting all installed packages.
        2. **Pip (`importlib.metadata.version()`)** - Fallback for retrieving individual package metadata.
        3. **Homebrew (`brew list --versions`)** - If applicable on macOS.
        4. **APT/DNF (`dpkg -s` or `rpm -q`)** - If applicable on Linux.
        5. **Windows Package Manager (`powershell Get-AppxPackage`)** - If applicable on Windows.

    ## Args:
        - `package` (`str`): The package name to check.
        - `configs` (`dict`): Configuration dictionary containing system environment details.

    ## Returns:
        - `Optional[str]`: The installed package version if found, otherwise `None`.

    ## Notes:
        - Uses structured logging to track package version retrieval.
        - Ensures compatibility with externally managed Python environments.
    """

    env = configs.get("environment", {})
    install_method = env.get("INSTALL_METHOD")

    debug_package = f'[DEBUG]   Package "{package}"'

    # Check Pip First (Preferred)
    if not env.get("EXTERNALLY_MANAGED", False):  # Only check Pip if not externally managed
        try:
            # Fetch list of installed packages in JSON format
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )

            installed_packages = json.loads(result.stdout)
            package_versions = {pkg["name"].lower(): pkg["version"] for pkg in installed_packages}

            if package.lower() in package_versions:
                version = package_versions[package.lower()]
                log_utils.log_message(
                    f'{debug_package} detected via Pip list: {version}',
                    environment.category.debug.id,
                    configs=configs
                )
                return version
            else:
                log_utils.log_message(
                    f'{debug_package} NOT found via Pip list.',
                    environment.category.debug.id,
                    configs=configs
                )

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            log_utils.log_message(
                f'[ERROR] Pip list failed: {e}',
                configs=configs
            )

    # If not found, fallback to `importlib.metadata.version()`
    try:
        version = importlib.metadata.version(package)
        log_utils.log_message(
            f'\n{debug_package} detected via importlib: {version}',
            environment.category.debug.id,
            configs=configs
        )
        return version
    except importlib.metadata.PackageNotFoundError:
        log_utils.log_message(
            f'{debug_package} NOT found via importlib.',
            environment.category.debug.id,
            configs=configs
        )

    debug_checking = f'[DEBUG]   Checking "{package}"'
    # Use the correct package manager based on INSTALL_METHOD
    match install_method:
        case "brew":
            version = brew_utils.version(package)
            log_utils.log_message(
                f'{debug_checking} via Brew: {version}',
                environment.category.debug.id,
                configs=configs
            )
            return version

        case "system":
            version = linux_version(package)
            log_utils.log_message(
                f'{debug_checking} via APT/DNF: {version}',
                environment.category.debug.id,
                configs=configs
            )
            return version

        case "microsoft_store":
            version = windows_version(package)
            log_utils.log_message(
                f'{debug_checking} via Microsoft Store: {version}',
                environment.category.debug.id,
                configs=configs
            )
            return version

    error_package = f'[ERROR] Package "{package}"'
    log_utils.log_message(
        f'{error_package} was NOT found in any method!',
        environment.category.error.id,
        configs=configs
    )

    return None  # Package not found via any method

## -----------------------------------------------------------------------------

def pip_latest_version(package: str) -> Optional[str]:
    """
    Retrieve the latest available version of a package via Pip.

    This function executes `pip index versions <package>` to fetch a list of available
    versions and extracts the latest one.

    ## Args:
        - `package` (`str`): The package name to check.

    ## Returns:
        - `Optional[str]`: The latest available version as a string if found, otherwise `None`.

    ## Notes:
        - Requires internet access to fetch version information from PyPI.
    """

    try:
        result = subprocess.run(
            [ sys.executable, "-m", "pip", "index", "versions", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "Available versions:" in line:
                versions = line.split(":")[1].strip().split(", ")
                return versions[0] if versions and versions[0] != "None" else None  # ✅ Ensure `NoneType` is returned properly
    except subprocess.CalledProcessError:
        return None
