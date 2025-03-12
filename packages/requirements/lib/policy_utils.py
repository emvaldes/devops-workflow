#!/usr/bin/env python3

# File: ./packages/requirements/lib/policy_utils.py
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

from . import (
    package_utils,
    version_utils
)

## -----------------------------------------------------------------------------

def policy_management(configs: dict) -> list:

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
                version_info["status"] = "outdated"  # Wrong when installed == target
                log_message = f'{policy_header} matches target but a newer version ({available_ver}) is available. Marking as outdated.'
            else:
                version_info["status"] = "matched"  # Correct: If installed == target, it's "matched"
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

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
