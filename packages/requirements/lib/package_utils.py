#!/usr/bin/env python3

# File: ./packages/requirements/lib/package_utils.py
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

from . import version_utils

## -----------------------------------------------------------------------------

def backup_packages(file_path: str, configs: dict) -> None:

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

        # NEW: If force_install is True, override status to "adhoc"
        if bypass:
            status = "adhoc"

        # Policy-driven installation decisions
        if status == "installing" or status == "missing":
            log_utils.log_message(
                f'[INSTALL] Installing "{package}" ({"latest" if policy_mode == "latest" else target_version})...',
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
        # NEW: ELSE CLAUSE FOR FORCED INSTALLATION
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
                f'[INSTALL] Installing {package} ({"latest" if policy_mode == "latest" else target_version})...',
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

    # return configs.get("packages", {}).get("installation", {}).get("configs", None)
    try:
        installed_path = configs["packages"]["installation"]["configs"]
        return Path(installed_path) if isinstance(installed_path, str) else installed_path
    except KeyError:
        raise KeyError("Missing 'packages.installation.configs' in CONFIGS")

## -----------------------------------------------------------------------------

def migrate_packages(file_path: str, configs: dict) -> None:

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

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
