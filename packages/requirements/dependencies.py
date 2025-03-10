#!/usr/bin/env python3

# File: ./packages/requirements/dependencies.py
__version__ = "0.2.0"  ## Package version

"""
# Advanced Dependency Management System

## Overview
    This module serves as the core of the **AppFlow Tracer - Dependency Management System**,
    providing a structured and policy-driven approach to handling dependencies. It supports
    both **Homebrew (macOS)** and **Pip (cross-platform)** while ensuring package versioning
    compliance, safe installation policies, and structured logging.

## Features
    - **Environment Detection**: Determines how Python is installed (Homebrew, system package managers, or standalone).
    - **Package Management**: Handles installation, upgrades, downgrades, and compliance with predefined policies.
    - **Brew & Pip Integration**:
      - Uses **Homebrew** if Python is managed via Brew.
      - Uses **Pip** for all other installations, with safe installation handling.
    - **Policy-Based Installation**:
      - Installs missing packages.
      - Upgrades outdated packages to the latest version if policy allows.
      - Downgrades packages if policy enforces strict versioning.
    - **Logging & Debugging**:
      - Logs all package operations, warnings, and errors.
      - Provides structured debugging messages for troubleshooting.
    - **Backup & Restore**:
      - Saves the current list of installed packages for future restoration.
      - Allows migration of package environments.
    - **Package Status Reporting**:
      - Displays installed packages with versioning and compliance details.
      - Writes results into `installed.json` for tracking.

## Dependencies
    - `subprocess` - Runs Brew and Pip commands.
    - `argparse` - Parses command-line arguments.
    - `json` - Manages structured dependency files.
    - `importlib.metadata` - Fetches installed package versions.
    - `pathlib` - Ensures safe file path handling.
    - `functools.lru_cache` - Optimizes frequently accessed functions.
    - `brew_utils`, `package_utils`, `policy_utils`, `version_utils` - Sub-modules managing dependency operations.

## Sub-Modules
    - **`brew_utils.py`**:
      - Detects if Homebrew is available on macOS.
      - Retrieves installed and latest package versions from Homebrew.

    - **`package_utils.py`**:
      - Handles package installations using Brew or Pip.
      - Implements structured installation logic for policy-driven updates.

    - **`policy_utils.py`**:
      - Evaluates package policies (install, upgrade, downgrade, skip).
      - Updates `installed.json` to reflect policy-enforced status.

    - **`version_utils.py`**:
      - Fetches installed and latest available package versions.
      - Supports multi-platform version detection (Pip, Brew, APT, DNF, Windows Store).

## Expected Behavior
    - Dynamically adapts package installation based on system constraints.
    - Installs, upgrades, or downgrades packages per predefined policies.
    - Logs all package operations for debugging and troubleshooting.
    - Prevents unintended system modifications unless explicitly overridden (`--force`).

## Exit Codes
    - `0`: Execution completed successfully.
    - `1`: Failure due to installation errors, missing configurations, or dependency issues.

## Example Usage
    ### **Installing Dependencies**
    ```python
    from dependencies import package_utils
    package_utils.install_requirements(configs=configs)
"""

import sys
import subprocess
import shutil

import json
import argparse
import platform

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

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

# Import trace_utils from lib.*_utils
from .lib import (
    brew_utils,
    package_utils,
    policy_utils,
    version_utils
)

## -----------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for package management.

    This function provides command-line options for managing dependencies,
    allowing users to specify requirement files, enforce installations,
    backup, restore, or migrate packages.

    ## Supported Arguments:
        - `-c/--config`: Specify a custom JSON requirements file.
        - `-f/--force`: Force Pip installations using `--break-system-packages`.
        - `--backup-packages`: Save installed package list for future restoration.
        - `--restore-packages`: Restore packages from a backup file.
        - `--migrate-packages`: Migrate package environments.
        - `--show-installed`: Display installed dependencies.

    ## Args:
        - `None`

    Returns:
        - `argparse.Namespace`: The parsed arguments object containing selected options.

    Return Type: argparse.Namespace
        Returns an argparse.Namespace object containing the parsed command-line arguments.

    ## Notes:
        - This function is critical for enabling dynamic dependency management.
    """


    parser = argparse.ArgumentParser(
        description="Manage package dependencies using Brew and PIP using policy management."
                    "Use -c/--config to specify a custom JSON configuration file."
                    "Use -f/--force to request PIP to install using --break-system-packages."
                    "Use --backup-packages: Backup existing environment into packages-list."
                    "Use --restore-packages: Restore archived packages list into environment."
                    "Use --migrate-packages: Migrate legacy packages into new environment."
                    "Use --show-installed to display installed dependencies."
    )
    parser.add_argument(
        "-c", "--config",
        dest="requirements",
        default="./packages/requirements/requirements.json",
        help="Path to the requirements JSON file (default: ./packages/requirements/requirements.json)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force PIP installations (using --break-system-packages) in an externally-managed environment."
    )
    parser.add_argument(
        "-b", "--backup-packages",
        dest="backup_packages",
        default=None,  # Fix: Set to None
        help="Backup existing environment into a packages list"
    )
    parser.add_argument(
        "-r", "--restore-packages",
        dest="restore_packages",
        default=None,  # Fix: Set to None
        help="Restore archived packages list into environment"
    )
    parser.add_argument(
        "-m", "--migrate-packages",
        dest="migrate_packages",
        default=None,  # Fix: Set to None
        help="Migrate legacy packages into a new environment"
    )
    parser.add_argument(
        "--show-installed",
        action="store_true",
        help="Display the contents of installed.json"
    )
    return parser.parse_args()

## -----------------------------------------------------------------------------

def main() -> None:
    """
    Entry point for the dependency management system.

    This function initializes logging, processes command-line arguments,
    and installs or updates dependencies from a JSON requirements file.
    It dynamically determines the system's Python environment and applies
    installation policies accordingly.

    ## Workflow:
    1. **Parse Command-Line Arguments**
       - Loads configuration settings.
       - Determines runtime settings.

    2. **Load Requirements File**
       - Reads `requirements.json` (or custom-specified file).
       - Extracts dependency data.

    3. **Setup Logging & Environment**
       - Detects Python installation method.
       - Logs detected system information.

    4. **Handle Backup & Restore Operations**
       - Saves a package list for future restoration.
       - Restores or migrates package environments if specified.

    5. **Determine Dependency Policies**
       - Calls `policy_utils.policy_management()` to enforce package rules.

    6. **Install Dependencies**
       - Uses `package_utils.install_requirements()` for installations.

    7. **Display Installed Packages (if requested)**
       - Shows structured package information from `installed.json`.

    ## Args:
    - `None`

    ## Returns:
    - `None`: This function performs actions based on command-line arguments and manages dependencies.

    ## Notes:
    - If an error occurs (e.g., missing `requirements.json`), the process will exit with `sys.exit(1)`.
    - The function prevents breaking system-managed environments unless explicitly overridden (`--force`).
    """

    # Ensure the variable exists globally
    global CONFIGS

    args = parse_arguments()

    # CONFIGS = tracing.setup_logging(events=False)
    CONFIGS = tracing.setup_logging(events=["call", "return"])

    # Load the JSON file contents before passing to policy_utils.policy_management
    location = Path(args.requirements)
    if not location.exists():
        log_utils.log_message(
            f'Error: Requirements file not found at {location}',
            environment.category.error.id,
            configs=CONFIGS
        )
        sys.exit(1)

    with location.open("r") as f:
        CONFIGS["requirements"] = json.load(f).get("dependencies", [])

    log_utils.log_message(
        f'\nInitializing Package Dependencies Management process...',
        configs=CONFIGS
    )

    # Get the directory of `requirements.json`
    # installed_filepath = str(location.parent / "installed.json")  # Ensure it's always a string
    installed_filepath = location.parent / "installed.json"  # Ensures the correct file path

    # Ensure the file exists; if not, create an empty JSON object
    if not installed_filepath.exists():
        log_utils.log_message(
            f'[INFO] Creating missing installed.json at {installed_filepath}',
            configs=CONFIGS
        )
        installed_filepath.parent.mkdir(
            parents=True,
            exist_ok=True
        )  # Ensure directory exists
        with installed_filepath.open("w") as f:
            json.dump({}, f, indent=4)  # Create empty JSON object

    # Ensure 'packages' structure exists in CONFIGS
    CONFIGS.setdefault( "packages", {} ).setdefault(
        "installation", { "forced": args.force, "configs": installed_filepath }
    )

    if args.backup_packages is not None:
        log_utils.log_message(
            f'[INFO] Running backup with file: "{args.backup_packages}"',
            environment.category.info.id,
            configs=CONFIGS
        )
        package_utils.backup_packages(
            file_path=args.backup_packages,
            configs=CONFIGS
        )

    if args.restore_packages is not None:
        log_utils.log_message(
            f'[INFO] Running restore from file: "{args.restore_packages}"',
            environment.category.info.id,
            configs=CONFIGS
        )
        package_utils.restore_packages(
            file_path=args.restore_packages,
            configs=CONFIGS
        )

    if args.migrate_packages is not None:
        log_utils.log_message(
            f'[INFO] Running migration and saving to file: "{args.migrate_packages}"',
            environment.category.info.id,
            configs=CONFIGS
        )
        package_utils.migrate_packages(
            file_path=args.migrate_packages,
            configs=CONFIGS
        )

    if args.show_installed:
        if installed_filepath.exists():
            with installed_filepath.open("r") as f:
                print(json.dumps(json.load(f), indent=4))
        else:
            log_utils.log_message(
                f'[INFO] Configuration: {installed_filepath} was not found.',
                environment.category.info.id,
                configs=CONFIGS
            )
        return  # Exit after showing installed packages

    environment_info = brew_utils.detect_environment()
    log_utils.log_message(
        f'\n[ENVIRONMENT] Detected Python Environment: {json.dumps(environment_info, indent=4)}',
        configs=CONFIGS
    )

    CONFIGS.setdefault("environment", {}).update(environment_info)

    CONFIGS["requirements"] = policy_utils.policy_management(
        configs=CONFIGS
    )

    CONFIGS["requirements"] = package_utils.install_requirements( configs=CONFIGS )

    print(
        f'CONFIGS:\n',
        f'{json.dumps(CONFIGS, indent=environment.default_indent, default=str)}'
    )

    # log_utils.log_message(
    #     f'Logs are being saved in: {CONFIGS["logging"].get("log_filename")}',
    #     configs=CONFIGS
    # )

if __name__ == "__main__":
    main()
