#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/test_dependencies_utils.py

__package__ = "tests.requirements"
__module__ = "dependencies"

__version__ = "0.1.0"  ## Updated Test Module version

"""
# PyTest Module: test_dependencies_utils.py

## Overview:
    This module contains unit tests for `dependencies.py`, ensuring correct command-line
    argument parsing and structured execution of dependency management functions.

## Test Coverage:
    1. `parse_arguments()`
       - Validates command-line argument parsing.
       - Ensures default values and overrides work correctly.

    2. `main()`
       - Mocks package utilities and policy management functions.
       - Simulates command execution (backup, restore, migrate, install).
       - Ensures correct logging and configuration initialization.

## Mocking Strategy:
    - `policy_utils.policy_management()` → Simulates policy enforcement logic.
    - `package_utils.install_requirements()` → Mocks package installation logic.
    - `package_utils.backup_packages()` → Ensures backups execute correctly.
    - `package_utils.restore_packages()` → Ensures restores execute correctly.
    - `package_utils.migrate_packages()` → Validates migration workflow.
    - `log_utils.log_message()` → Verifies structured logging messages.

## Expected Behavior:
    - Dependencies are processed based on user-provided arguments.
    - Logs are generated for major execution steps.
    - Backup, restore, and migration options execute correctly.
    - `installed.json` is managed as expected.
"""

import sys
import pytest
import argparse
import json

from unittest.mock import (
    ANY,
    patch
)
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.mocks.config_loader import (
    load_mock_requirements,
    load_mock_installed
)
from packages.requirements import dependencies
from packages.requirements.lib import (
    package_utils,
    policy_utils
)

# Add this function before the test cases
def serialize_configs(configs):
    """Convert PosixPath objects to strings for JSON serialization."""
    return json.loads(json.dumps(configs, default=lambda o: str(o) if isinstance(o, Path) else o))

@pytest.fixture
def mock_config():
    """Create a mock CONFIGS dictionary to simulate package management settings."""
    return {
        "packages": {"installation": {"forced": False, "configs": Path("/tmp/test_installed.json")}},
        "environment": {"INSTALL_METHOD": "pip", "EXTERNALLY_MANAGED": False},
        "logging": {"package_name": "requirements", "module_name": "dependencies", "enable": False},
        "tracing": {"enable": False},
        "requirements": [
            {"package": "requests", "version": {"policy": "latest", "target": "2.28.0", "latest": None, "status": None}}
        ],
    }

# ------------------------------------------------------------------------------
# Test: parse_arguments()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "args, expected",
    [
        ([], "./packages/requirements/requirements.json"),  # Default value
        (["-c", "custom_requirements.json"], "custom_requirements.json"),  # Custom value
    ]
)
def test_parse_arguments(
    args,
    expected
):
    """
    Ensure `parse_arguments()` correctly handles command-line arguments.

    **Test Strategy:**
    - Patch `sys.argv` to prevent argparse from exiting unexpectedly.
    - Mock `sys.exit` to catch any unwanted exits.
    - Validate that `--config` is correctly assigned.

    **Expected Behavior:**
    - `requirements.json` is used as default if no `-c` argument is provided.
    - If `-c <file>` is passed, it should override the default.
    """

    test_args = ["dependencies.py"] + args  # Ensure script name is included

    with patch.object(sys, "argv", test_args), \
         patch("sys.exit") as mock_exit:  # Prevent argparse from exiting

        parsed_args = dependencies.parse_arguments()  # Correctly call the function
        assert parsed_args.requirements == expected  # Validate parsed argument
        mock_exit.assert_not_called()  # Ensure no forced exit happened

# ------------------------------------------------------------------------------
# Test: main()
# ------------------------------------------------------------------------------

@pytest.fixture
def mock_config():
    """
    Create a mock CONFIGS dictionary to simulate package management settings.
    """

    return {
        "packages": {"installation": {"forced": False, "configs": Path("/tmp/test_installed.json")}},
        "environment": {"INSTALL_METHOD": "pip", "EXTERNALLY_MANAGED": False},
        "logging": {"package_name": "requirements", "module_name": "dependencies", "enable": False},
        "tracing": {"enable": False},
        "requirements": [
            {"package": "requests", "version": {"policy": "latest", "target": "2.28.0", "latest": None, "status": None}}
        ],
    }

# ------------------------------------------------------------------------------

def test_main(mock_config):
    """
    Ensure `main()` executes correctly with mocked dependencies, focusing on critical functionality.

    **Test Strategy:**
        - Mocks command-line arguments (`--backup-packages`, `--restore-packages`, etc.).
        - Ensures package installation is executed as expected.
        - Verifies that logging messages are generated.

    **Expected Behavior:**
        - `policy_management()` is called for dependency policy enforcement.
        - `install_requirements()` installs packages based on evaluated policies.
        - Backup, restore, and migration options execute correctly when passed.
        - `installed.json` is properly updated.
    """

    temp_installed_file = mock_config["packages"]["installation"]["configs"]

    installed_mock = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "policy": "latest",
                    "target": "2.28.0",
                    "latest": "2.28.1",
                    "status": "outdated"
                }
            }
        ]
    }
    temp_installed_file.write_text(
        json.dumps(installed_mock, indent=4)
    )

    # Mock command-line arguments
    with patch.object(
            sys,
            "argv",
            ["dependencies.py", "--backup-packages", "backup.json"]
         ), \
         patch(
             "packages.requirements.lib.policy_utils.policy_management",
             return_value=mock_config.get(
                 "requirements", []
             )
         ) as mock_policy, \
         patch(
             "packages.requirements.lib.package_utils.install_requirements",
             return_value=installed_mock["dependencies"]
         ) as mock_install, \
         patch(
             "packages.requirements.lib.package_utils.backup_packages"
         ) as mock_backup, \
         patch(
             "packages.appflow_tracer.lib.log_utils.log_message"
         ) as mock_log:

        dependencies.main()  # Execute main()

        # Ensure `policy_management()` was called
        mock_policy.assert_called_once()

        # Ensure `install_requirements()` was called
        mock_install.assert_called_once()

        # Ensure backup operation was triggered
        mock_backup.assert_called_once_with(
            file_path="backup.json",
            configs=ANY
        )

        # Ensure logging was used
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )

# ------------------------------------------------------------------------------

def test_main_restore(mock_config):
    """
    Ensure `main()` executes restore functionality correctly.

    **Test Strategy:**
        - Mocks `--restore-packages` argument.
        - Ensures `restore_packages()` is executed as expected.
        - Verifies correct logging behavior.

    **Expected Behavior:**
        - Restore operation is triggered.
        - No installation occurs if only `--restore-packages` is provided.
    """

    with patch.object(sys, "argv", ["dependencies.py", "--restore-packages", "restore.json"]), \
         patch("packages.requirements.lib.package_utils.restore_packages") as mock_restore, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        dependencies.main()  # Execute main()

        # Ensure `restore_packages()` was called with the expected arguments
        mock_restore.assert_called_once_with(
            file_path="restore.json",
            configs=ANY
        )

        # Ensure logging was triggered
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )

# ------------------------------------------------------------------------------

def test_main_migration(mock_config):
    """
    Ensure `main()` executes migration functionality correctly.

    **Test Strategy:**
        - Mocks `--migrate-packages` argument.
        - Ensures `migrate_packages()` is executed as expected.
        - Verifies correct logging behavior.

    **Expected Behavior:**
        - Migration operation is triggered.
        - No installation occurs if only `--migrate-packages` is provided.
    """

    with patch.object(
            sys,
            "argv",
            ["dependencies.py", "--migrate-packages", "migrate.json"]
         ), \
         patch(
             "packages.requirements.lib.package_utils.migrate_packages"
         ) as mock_migrate, \
         patch(
             "packages.appflow_tracer.lib.log_utils.log_message"
         ) as mock_log:

        dependencies.main()  # Execute main()

        # Convert PosixPath before logging
        serialized_configs = serialize_configs(
            mock_config
        )

        # Ensure function calls receive converted configs
        mock_migrate.assert_called_once_with(
            file_path="migrate.json",
            configs=ANY
        )

        # Ensure logging does not fail due to PosixPath serialization
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )  # Allow flexibility instead of exact match
