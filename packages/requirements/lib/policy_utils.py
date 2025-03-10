#!/usr/bin/env python3

# File: ./packages/requirements/lib/policy_utils.py
# Version: 0.1.0

"""
# Environment and Policy Management Utilities

## Overview
    This module provides functions for managing package policies and evaluating dependency
    installation requirements within the dependency management system. It ensures that packages
    are installed, upgraded, or downgraded based on predefined policies while maintaining compliance
    with system constraints.

## Features
    - **Policy-Based Dependency Evaluation:** Determines whether a package should be installed, upgraded, downgraded, or skipped.
    - **Automated Compliance Checking:** Compares installed versions against target and latest versions.
    - **Dynamic Policy Enforcement:** Adapts installation actions based on policies such as `"latest"` or `"restricted"`.
    - **Structured Logging:** Provides detailed debugging and compliance logs for better traceability.
    - **Integration with Installed Package Records:** Updates `installed.json` dynamically.

## Usage
This module is invoked by the dependency management workflow to analyze package states and
apply policy-driven installation decisions.

## Dependencies
    - `subprocess`: For executing system commands.
    - `json`: For handling structured package configurations.
    - `platform`: For system detection.
    - `importlib.metadata`: For retrieving installed package versions.
    - `pathlib`: For managing configuration file paths.
    - `log_utils`: Custom logging module for structured output.
    - `package_utils`: Provides package management functions such as retrieving `installed.json`.
    - `version_utils`: Handles installed and latest package version retrieval.

## Notes
    - This module ensures a **structured decision-making** process for package installations.
    - It dynamically adapts to the system's constraints, ensuring **safe package management**.
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

from . import (
    package_utils,
    version_utils
)

## -----------------------------------------------------------------------------

def policy_management(configs: dict) -> list:
    """
    Evaluate package installation policies and update dependency statuses.

    This function analyzes each package in the dependency list, comparing its installed
    version against the target and latest available versions. Based on the specified
    policy, it determines whether the package should be installed, upgraded, downgraded,
    or skipped.

    ## Args:
        - `configs` (`dict`): The configuration dictionary containing dependency policies.

    ## Returns:
        - `list`: The updated list of dependencies with policy-based statuses.

    ## Policy Decision Logic:
        1. **Missing Package (`status = "installing"`)**
           - If the package is not installed, it is marked for installation.
           - Installs either the `"latest"` or `"target"` version based on policy.

        2. **Outdated Package (`status = "outdated" | "upgrading"`)**
           - If installed version < target version:
             - `"latest"` policy → Upgrade to latest available version.
             - `"restricted"` policy → Keep outdated but log warning.

        3. **Target Version Matched (`status = "matched"`)**
           - If installed version == target version:
             - `"latest"` policy → Check if a newer version exists; mark as `"outdated"`.
             - Otherwise, mark as `"matched"` (no action needed).

        4. **Upgraded Version Installed (`status = "downgraded" | "upgraded"`)**
           - If installed version > target version:
             - `"restricted"` policy → Downgrade to target version.
             - `"latest"` policy → Keep upgraded.

    ## Logging:
        - Each package's evaluation is logged, showing its target, installed, and latest versions.
        - Policy enforcement decisions are logged with detailed status messages.

    ## Notes:
        - This function modifies `configs["requirements"]` and updates `installed.json`.
        - Ensures structured compliance before initiating installation processes.
    """

    dependencies = configs["requirements"]  # Use already-loaded requirements
    installed_filepath = package_utils.installed_configfile(configs)  # Fetch dynamically

    for dep in dependencies:
        package = dep["package"]
        version_info = dep["version"]

        policy_mode = version_info.get("policy", "latest")  # Default to "latest"
        target_version = version_info.get("target")

        installed_ver = version_utils.installed_version(package, configs)  # Get installed version
        available_ver = version_utils.latest_version(package, configs)  # Get latest available version

        # Update version keys in `CONFIGS["requirements"]`
        version_info["latest"] = available_ver  # Store the latest available version
        version_info["status"] = False  # Default status before processing

        # # Debugging
        # Collect log messages in a list
        log_messages = [
            f'[DEBUG]   Evaluating package: {package}',
            f'          Target Version : {target_version}',
            f'          Installed Ver. : {installed_ver if installed_ver else "Not Installed"}',
            f'          Latest Ver.    : {available_ver if available_ver else "Unknown"}',
            f'          Policy Mode    : {policy_mode}'
        ]

        # Convert list into a single string and log it
        log_utils.log_message(
            "\n".join(log_messages),
            environment.category.debug.id,
            configs=configs
        )

        policy_header = f'[POLICY]  Package "{package}"'
        log_message = ""

        # Policy decision-making
        if not installed_ver:
            version_info["status"] = "installing"
            log_message = f'{policy_header} is missing. Installing {"latest" if policy_mode == "latest" else target_version}.'
        elif installed_ver < target_version:
            if policy_mode == "latest":
                version_info["status"] = "upgrading"
                log_message = f'{policy_header} is outdated ({installed_ver} < {target_version}). Upgrading...\n'
            else:
                version_info["status"] = "restricted"
                log_message = f'{policy_header} is below target ({installed_ver} < {target_version}), but policy is restricted.'

        # elif installed_ver == target_version:
        #     if policy_mode == "latest" and available_ver > installed_ver:
        #         version_info["status"] = "outdated"
        #         log_message = f'{policy_header} matches target but a newer version is available. Marking as outdated.'
        #     else:
        #         version_info["status"] = "matched"
        #         log_message = f'{policy_header} matches the target version. No action needed.'

        elif installed_ver == target_version:
            if policy_mode == "latest" and available_ver and available_ver > installed_ver:
                version_info["status"] = "outdated"  # ❌ Wrong when installed == target
                log_message = f'{policy_header} matches target but a newer version ({available_ver}) is available. Marking as outdated.'
            else:
                version_info["status"] = "matched"  # ✅ Correct: If installed == target, it's "matched"
                log_message = f'{policy_header} matches the target version. No action needed.'

        else:  # installed_ver > target_version
            if policy_mode == "restricted":
                version_info["status"] = "downgraded"
                log_message = f'{policy_header} is above target ({installed_ver} > {target_version}). Downgrading...'
            else:
                version_info["status"] = "upgraded"
                log_message = f'{policy_header} is above target but latest policy applies. Keeping as upgraded.'

        # Log once per package
        if log_message:
            log_utils.log_message(
                log_message,
                configs=configs
            )

    # Save modified `requirements` to `installed.json`
    try:
        with open(installed_filepath, "w") as f:
            json.dump({"dependencies": dependencies}, f, indent=4)
        log_message = f'\n[DEBUG]   Package Configuration updated at {installed_filepath}'
        log_utils.log_message(
            log_message,
            environment.category.debug.id,
            configs=configs
        )
    except Exception as e:
        error_message = f'[ERROR] Failed to write installed.json: {e}'
        log_utils.log_message(
            error_message,
            environment.category.error.id,
            configs=configs
        )

    return dependencies  # Explicitly return the modified requirements list
