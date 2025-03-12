#!/usr/bin/env python3

# File: ./packages/requirements/lib/version_utils.py
# Version: 0.1.0

# Standard library imports - Core system and OS interaction modules
import sys
import subprocess
import shutil

# Standard library imports - Utility modules
import json
import argparse
import platform
import logging

# Standard library imports - Import system
import importlib.metadata

# Standard library imports - Function tools
from functools import lru_cache

# Standard library imports - Date and time handling
from datetime import datetime, timezone

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Type hinting (kept in a separate group)
from typing import Optional, Union

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

from . import brew_utils

# ------------------------------------------------------

def latest_version(package: str, configs: dict) -> Optional[str]:

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

    try:
        result = subprocess.run(
            [ "powershell", "-Command", f'(Get-AppxPackage -Name {package}).Version' ],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        return version if version else None  # Return None if no output is found
    except subprocess.CalledProcessError:
        return None  # If the command fails, the package is missing

## -----------------------------------------------------------------------------

def windows_latest_version(package: str) -> Optional[str]:

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

    # # If not found, fallback to `importlib.metadata.version()`
    # try:
    #     version = importlib.metadata.version(package)
    #     log_utils.log_message(
    #         f'\n{debug_package} detected via importlib: {version}',
    #         environment.category.debug.id,
    #         configs=configs
    #     )
    #     return version
    # except importlib.metadata.PackageNotFoundError:
    #     log_utils.log_message(
    #         f'{debug_package} NOT found via importlib.',
    #         environment.category.debug.id,
    #         configs=configs
    #     )
    #     return "not installed"  # Ensure we return a value instead of None
    # except KeyError:  # Handle missing 'Version' field explicitly
    #     log_utils.log_message(
    #         f'{debug_package} metadata exists but lacks a version field.',
    #         environment.category.debug.id,
    #         configs=configs
    #     )
    #     return "unknown"  # Avoid crash when 'Version' field is missing

    # try:
    #     version = importlib.metadata.version(package)
    #
    #     if not version:  # ✅ Covers both None and empty string cases
    #         raise importlib.metadata.PackageNotFoundError  # ✅ Raise the correct exception
    #
    #     log_utils.log_message(
    #         f'\n{debug_package} detected via importlib: {version}',
    #         environment.category.debug.id,
    #         configs=configs
    #     )
    #     return version
    #
    # except (importlib.metadata.PackageNotFoundError, KeyError):  # ✅ Catch both exceptions properly
    #     log_utils.log_message(
    #         f'{debug_package} NOT found via importlib or missing version field.',
    #         environment.category.debug.id,
    #         configs=configs
    #     )
    #     return None  # ✅ Ensures None is returned correctly

    try:
        dist = importlib.metadata.distribution(package)  # ✅ Fetch distribution first

        if "Version" in dist.metadata:  # ✅ Explicitly check if "Version" exists
            version = dist.metadata["Version"]

            log_utils.log_message(
                f'\n{debug_package} detected via importlib: {version}',
                environment.category.debug.id,
                configs=configs
            )
            return version
        else:
            log_utils.log_message(
                f'{debug_package} metadata exists but lacks a version field.',
                environment.category.debug.id,
                configs=configs
            )
            return None  # ✅ Return None if "Version" is missing

    except importlib.metadata.PackageNotFoundError:
        log_utils.log_message(
            f'{debug_package} NOT found via importlib.',
            environment.category.debug.id,
            configs=configs
        )
        return None  # ✅ Ensures proper return when package is missing

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
                return versions[0] if versions and versions[0] != "None" else None  # Ensure `NoneType` is returned properly
    except subprocess.CalledProcessError:
        return None

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
