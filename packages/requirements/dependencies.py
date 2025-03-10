#!/usr/bin/env python3

# File: ./packages/requirements/dependencies.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system and OS interaction modules
import sys
import subprocess
import shutil

# Standard library imports - Utility modules
import json
import argparse
import platform

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

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()
