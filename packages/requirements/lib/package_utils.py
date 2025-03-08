#!/usr/bin/env python3

# File: ./packages/requirements/lib/package_utils.py
# Version: 0.1.0

"""
# Package Management Utilities for Dependency Handling

## Overview
    This module provides utility functions for managing Python package dependencies in a structured
    and policy-driven approach. It facilitates installing, backing up, restoring, and reviewing package
    versions while ensuring compliance with system constraints.

## Features
    - **Backup & Restore Packages:** Saves and restores installed packages for migration or disaster recovery.
    - **Policy-Based Package Installation:** Handles installation, upgrades, and downgrades based on predefined policies.
    - **Dependency Review & Management:** Evaluates installed versions against required versions and logs compliance.
    - **Homebrew & Pip Integration:** Uses Homebrew if applicable, otherwise falls back to Pip with appropriate safeguards.
    - **Logging & Configuration Handling:** Ensures structured logging and configuration retrieval.

## Usage
    This module is primarily used by the dependency management system to enforce structured package installations
    and compliance checks.

## Dependencies
    - `subprocess`: For executing Pip and Homebrew commands.
    - `json`: For handling structured dependency configurations.
    - `importlib.metadata`: For retrieving installed package versions.
    - `shutil`: To check for external utilities.
    - `pathlib`: For managing file paths.
    - `functools.lru_cache`: To optimize repetitive queries.
    - `log_utils`: Custom logging module for structured output.

## Notes
    - The module respects externally managed Python environments, ensuring system integrity.
    - It dynamically detects installation methods and applies package management policies accordingly.
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

from . import version_utils

## -----------------------------------------------------------------------------

def backup_packages(file_path: str, configs: dict) -> None:
    """
    Back up all installed Python packages to a requirements-style list.

    This function generates a list of installed packages using `pip freeze`
    and saves it to the specified file for later restoration.

    ## Args:
        - `file_path` (`str`): The file path where the installed package list will be saved.
        - `configs` (`dict`): Configuration dictionary used for logging.

    ## Raises:
        - `subprocess.CalledProcessError`: If the `pip freeze` command fails.

    ## Notes:
        - This function is useful for backing up environments before upgrades.
        - The saved file can be used for migration or disaster recovery.
    """

    try:
        with open(file_path, "w") as f:
            subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                stdout=f,
                check=True
            )
        log_utils.log_message(
            f'[INFO] Installed packages list saved to {file_path}',
            environment.category.info.id,
            configs=configs
        )
    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'[WARNING] Failed to save installed packages: {e}',
            environment.category.warning.id,
            configs=configs
        )

## -----------------------------------------------------------------------------

def install_package(package: str, version: Optional[str] = None, configs: dict = None) -> None:
    """
    Install or update a package using Brew (if applicable) or Pip.

    This function installs a package using the preferred method:
        - If Python is installed via Homebrew and the package is available in Brew, it uses `brew install`.
        - Otherwise, it falls back to Pip, considering:
          - `--user` for standalone installations.
          - `--break-system-packages` if the system is externally managed and forced installation is enabled.
          - Otherwise, prints manual installation instructions.

    ## Args:
        - `package` (`str`): The package name to install.
        - `version` (`Optional[str]`): The specific version to install (default: latest).
        - `configs` (`dict`): Configuration dictionary for logging and environment handling.

    ## Returns:
        - `None`: Executes the package installation process.

    ## Notes:
        - Ensures safe installation, respecting system constraints.
        - Uses structured logging to report installation status.
    """

    # Fetch environment details
    env_info = configs.get("environment", {})
    brew_available = env_info.get("INSTALL_METHOD") == "brew"  # Python is managed via Brew
    externally_managed = env_info.get("EXTERNALLY_MANAGED", False)  # Check if Pip is restricted
    forced_install = configs.get("packages", {}).get("installation", {}).get("forced", False)

    # Check if Brew is available & controls Python
    if brew_available:
        log_utils.log_message(
            f'[INFO]    Checking if "{package}" is available via Homebrew...',
            configs=configs
        )
        brew_list = subprocess.run(
            ["brew", "info", package],
            capture_output=True,
            text=True
        )

        if "Error:" not in brew_list.stderr:
            # If Brew has the package, install it
            log_utils.log_message(
                f'\n[INSTALL] Installing "{package}" via Homebrew...',
                environment.category.error.id,
                configs=configs
            )
            subprocess.run(["brew", "install", package], check=False)
            return
        else:
            log_utils.log_message(
                f'[WARNING] Package "{package}" is not available via Brew. Falling back to Pip...',
                configs=configs
            )

    # Use Pip (if Brew is not managing Python OR package not found in Brew)
    pip_install_cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--user"]

    if version:
        pip_install_cmd.append(f'{package}=={version}')
    else:
        pip_install_cmd.append(package)

    if externally_managed:
        # 2A: Pip is restricted → Handle controlled environment
        if forced_install:
            log_utils.log_message(
                f'[INSTALL] Installing "{package}" via Pip using `--break-system-packages` (forced mode)...',
                environment.category.error.id,
                configs=configs
            )
            pip_install_cmd.append("--break-system-packages")
            subprocess.run(pip_install_cmd, check=False)
        else:
            log_utils.log_message(
                f'[INFO]    Package "{package}" requires installation via Pip in a controlled environment.\n'
                f'\nRun the following command manually if needed:\n'
                f'    {sys.executable} -m pip install --user {package}',
                configs=configs
            )
    else:
        # 2B: Normal Pip installation (default)
        log_utils.log_message(
            f'[INSTALL] Installing "{package}" via Pip (default mode)...',
            environment.category.error.id,
            configs=configs
        )
        subprocess.run(pip_install_cmd, check=False)

    return  # Exit after installation

## -----------------------------------------------------------------------------

def install_requirements(configs: dict, bypass: bool = False) -> None:
    """
    Install, upgrade, or downgrade dependencies based on policy rules.

    This function processes dependencies listed in `configs["requirements"]` and applies
    necessary package actions (install, upgrade, downgrade). It first retrieves evaluated
    package statuses using `review_packages()`, ensuring a structured decision-making process.

    ## Args:
        - `configs` (`dict`): Configuration dictionary containing dependency requirements.
        - `force_install` (`bool`): If True, all packages are installed immediately, ignoring policy.

    ## Returns:
        - `None`: Executes the required package installations.

    ## Notes:
        - This function enforces policy-based installation to maintain package consistency.
        - It minimizes unnecessary installations by checking existing versions before applying changes.
        - Dependencies are installed using either Brew or Pip, based on system constraints.
    """

    log_utils.log_message(
        f'\n[INSTALL] Starting installation process...',
        environment.category.error.id,
        configs=configs
    )

    installed_filepath = installed_configfile(configs)
    if not installed_filepath.exists():
        log_utils.log_message(
            f'[ERROR] Missing installed.json path in CONFIGS.',
            configs=configs
        )
        sys.exit(1)  # Exit to prevent further failures

    # Use `review_packages()` to get the evaluated package statuses
    reviewed_packages = review_packages(configs)

    for dep in reviewed_packages:
        package = dep["package"]
        version_info = dep["version"]
        status = version_info["status"]
        target_version = version_info["target"]
        latest_version = version_info["latest"]
        policy_mode = version_info["policy"]

        # ✅ NEW: If force_install is True, override status to "adhoc"
        if bypass:
            status = "adhoc"

        # Policy-driven installation decisions
        if status == "installing" or status == "missing":
            log_utils.log_message(
                f'[INSTALL] Installing "{package}" ({'latest' if policy_mode == 'latest' else target_version})...',
                environment.category.error.id,
                configs=configs
            )
            install_package(
                package,
                latest_version if policy_mode == "latest" else target_version,
                configs
            )

        elif status == "upgrading" or status == "outdated":
            log_utils.log_message(
                f'\n[UPGRADE] Upgrading "{package}" to latest version ({latest_version})...',
                configs=configs
            )
            install_package(package, None, configs)  # None means latest

        elif status == "downgraded" or (status == "upgraded" and policy_mode == "enforce"):
            log_utils.log_message(
                f'[DOWNGRADE] Downgrading "{package}" to {target_version}...',
                configs=configs
            )
            install_package(package, target_version, configs)

        elif status in ["restricted", "matched"]:
            log_utils.log_message(
                f'[SKIP]    Skipping "{package}" is {status}, no changes needed.',
                environment.category.warning.id,
                configs=configs
            )
        # ✅ NEW: ELSE CLAUSE FOR FORCED INSTALLATION
        else:
            log_utils.log_message(
                f'[AD-HOC] Forcing "{package}" installation (bypassing policy checks) ...',
                configs=configs
            )
            install_package(package, None, configs)

    # Write back to `installed.json` **only once** after processing all packages
    with installed_filepath.open("w") as f:
        json.dump({ "dependencies": reviewed_packages }, f, indent=4)

    log_utils.log_message(
        f'\n[INSTALL] Package Configuration updated at {installed_filepath}',
        environment.category.error.id,
        configs=configs
    )
    log_utils.log_message(
        f'\n[INSTALL] Installation process completed.\n',
        environment.category.error.id,
        configs=configs
    )

    return reviewed_packages

## -----------------------------------------------------------------------------

def install_requirements__legacy(configs: dict) -> None:
    """
    Retrieve the path to `installed.json` from the configuration dictionary.

    This function extracts the configured path where installed package statuses are stored.

    ## Args:
        - `configs` (`dict`): The configuration dictionary.

    ## Returns:
        - `Path`: The resolved path to `installed.json`, or `None` if not configured.

    ## Notes:
        - This function ensures consistent access to installed package records.
    """

    log_utils.log_message(
        f'\n[INSTALL] Starting installation process...',
        environment.category.error.id,
        configs=configs
    )

    installed_filepath = installed_configfile(configs)  # Fetch dynamically
    if not installed_filepath.exists():
        log_utils.log_message(
            f'[ERROR] Missing installed.json path in CONFIGS.',
            configs=configs
        )
        sys.exit(1)  # Exit to prevent further failures

    # Use the `requirements` list from `CONFIGS`
    requirements = configs["requirements"]

    for dep in requirements:
        package = dep["package"]
        version_info = dep["version"]
        status = version_info["status"]
        target_version = version_info["target"]
        latest_version = version_info["latest"]
        policy_mode = version_info["policy"]

        if status == "installing":
            log_utils.log_message(
                f'[INSTALL] Installing {package} ({'latest' if policy_mode == 'latest' else target_version})...',
                environment.category.error.id,
                configs=configs
            )
            install_package(
                package,
                latest_version if policy_mode == "latest" else target_version,
                configs
            )

        elif status == "upgrading":
            log_utils.log_message(
                f'\n[UPGRADE] Upgrading "{package}" to latest version ({latest_version})...',
                configs=configs
            )
            install_package(package, None, configs)  # None means latest

        elif status == "downgraded":
            log_utils.log_message(
                f'[DOWNGRADE] Downgrading "{package}" to {target_version}...',
                configs=configs
            )
            install_package(package, target_version, configs)

        elif status in ["restricted", "matched"]:
            log_utils.log_message(
                f'[SKIP]    Skipping "{package}" is {status}, no changes needed.',
                environment.category.warning.id,
                configs=configs
            )

    # Write back to `installed.json` **only once** after processing all packages
    with installed_filepath.open("w") as f:
        json.dump({ "dependencies": requirements }, f, indent=4)

    log_utils.log_message(
        f'\n[INSTALL] Package Configuration updated at {installed_filepath}',
        environment.category.error.id,
        configs=configs
    )
    log_utils.log_message(
        f'\n[INSTALL] Installation process completed.\n',
        environment.category.error.id,
        configs=configs
    )

## -----------------------------------------------------------------------------

def installed_configfile(configs: dict) -> Path:
    """
    Migrate installed packages from the current Python environment to a new one.

    This function retrieves the list of installed packages using `pip list --format=freeze`,
    saves it to the specified file, and reinstalls each package in the new environment.

    ## Args:
        - `file_path` (`str`): The file path where the package list will be saved.
        - `configs` (`dict`): Configuration dictionary used for logging.

    ## Raises:
        - `subprocess.CalledProcessError`: If retrieving the package list fails.

    ## Notes:
        - The migration process ensures a smooth transition between Python versions or environments.
        - Before reinstalling, the function saves the package list for reference.
    """

    return configs.get("packages", {}).get("installation", {}).get("configs", None)

## -----------------------------------------------------------------------------

def migrate_packages(file_path: str, configs: dict) -> None:
    """
    Review installed package versions and return an updated package status list.

    This function checks all installed dependencies, compares them against target versions,
    determines their status (installed, outdated, missing), and returns a structured package list.

    ## Args:
        - `configs` (`dict`): The configuration dictionary containing dependency policies.

    ## Returns:
        - `list`: A structured list of reviewed packages, including installation status.

    ## Notes:
        - The function also updates `installed.json` with the latest package states.
        - Ensures a structured package evaluation process before applying changes.
    """

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        installed_packages = result.stdout.splitlines()

        # Save package list before migration
        with open(file_path, "w") as f:
            f.write("\n".join(installed_packages))

        for package in installed_packages:
            pkg_name = package.split("==")[0]
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", pkg_name],
                check=False
            )

        log_utils.log_message(
            f'[INFO] Packages have been migrated and the list is saved to {file_path}.',
            environment.category.info.id,
            configs=configs
        )

    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'[WARNING] Failed to migrate packages: {e}',
            environment.category.info.id,
            configs=configs
        )

## -----------------------------------------------------------------------------

def packages_installed(configs: dict) -> None:
    """
    Prints the installed dependencies in a readable format.

    This function reads `installed.json` and logs package names, required versions,
    installed versions, and compliance status.

    Args:
        configs (dict): Configuration dictionary.

    Returns:
        None: Prints the installed package details.
    """

    installed_filepath = installed_configfile(configs)  # Fetch dynamically

    if not installed_filepath or not installed_filepath.exists():
        log_utils.log_message(
            f'[WARNING] Installed package file not found: {installed_filepath}',
            configs=configs
        )
        return

    try:
        with installed_filepath.open("r") as f:
            installed_data = json.load(f)

        dependencies = installed_data.get("dependencies", [])

        if not dependencies:
            log_utils.log_message(
                "[INFO] No installed packages found.",
                configs=configs
            )
            return

        log_utils.log_message("\n[INSTALLED PACKAGES]", configs=configs)

        for dep in dependencies:
            package = dep.get("package", "Unknown")
            target_version = dep.get("version", {}).get("target", "N/A")
            get_installed_version = dep.get("version", {}).get("latest", "Not Installed")
            status = dep.get("version", {}).get("status", "Unknown")

            log_utils.log_message(
                f'- {package} (Target: {target_version}, Installed: {get_installed_version}, Status: {status})',
                configs=configs
            )

    except json.JSONDecodeError:
        log_utils.log_message(
            f'[ERROR] Invalid JSON structure in {installed_filepath}.',
            configs=configs
        )

## -----------------------------------------------------------------------------

def restore_packages(file_path: str, configs: dict) -> None:
    """
    Restores all previously backed-up Python packages by reading
    the specified file and installing the packages listed in it.

    This function should be executed after upgrading Python to ensure that
    the same packages are available in the new Python environment.

    Args:
        file_path (str): The file path to the package list generated by `pip freeze`.

    Raises:
        subprocess.CalledProcessError: If the package installation fails.
    """

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "-r", file_path],
            check=True
        )
        log_utils.log_message(
            f'[INFO] Installed packages restored successfully from {file_path}.',
            environment.category.info.id,
            configs=configs
        )
    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'[WARNING] Failed to restore packages from {file_path}: {e}',
            environment.category.warning.id,
            configs=configs
        )

## -----------------------------------------------------------------------------

def review_packages(configs: dict) -> list:
    """
    Reviews installed package versions and returns an updated package status list.

    This function checks all installed dependencies, determines their status
    (installed, outdated, missing), and returns the structured package data.
    It also updates `installed.json` with the latest package states.

    Args:
        configs (dict): Configuration dictionary.

    Returns:
        list: A list of reviewed package data including installation status.
    """

    installed_filepath = installed_configfile(configs)

    dependencies = configs.get("requirements", [])  # Ensure it defaults to an empty list
    installed_data = []

    for dep in dependencies:
        package_name = dep["package"]
        package_policy = dep["version"]["policy"]
        target_version = dep["version"]["target"]

        installed_version = version_utils.installed_version(package_name, configs)

        # Determine package-name status
        if installed_version == target_version:
            status = "latest"
        elif installed_version and installed_version > target_version:
            status = "upgraded"
        elif installed_version and installed_version < target_version:
            status = "outdated"
        else:
            status = "missing"  # Package is not installed

        installed_data.append({
            "package": package_name,
            "version": {
                "policy": package_policy,
                "target": target_version,
                "latest": installed_version,
                "status": status
            }
        })

    # Write to installed.json **once** after processing all dependencies
    with open(installed_filepath, "w") as file:
        json.dump({"dependencies": installed_data}, file, indent=4)

    log_utils.log_message(
        f'\n[UPDATE]  Updated JSON Config with packages status in: {installed_filepath}',
        environment.category.error.id,
        configs=configs
    )

    return installed_data  # Return the structured package list
