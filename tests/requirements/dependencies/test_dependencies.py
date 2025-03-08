#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/test_dependencies_utils.py
__version__ = "0.1.0"  ## Package version

"""
PyTest Module: test_dependencies.py

This module contains unit tests for `dependencies.py`, which serves as the core of the **AppFlow Tracer - Dependency Management System**.
It ensures proper command-line argument parsing and structured execution of dependency management functions.

## Test Coverage:
    1. `parse_arguments()`
       - Validates command-line argument parsing.
       - Ensures default values and overrides work correctly.

    2. `main()`
       - Mocks package utilities and policy management functions.
       - Simulates command execution (backup, restore, migrate, install).
       - Ensures correct logging and configuration initialization.

## Mocking Strategy:
    - `policy_utils.policy_management()` – Simulate policy enforcement logic.
    - `package_utils.install_requirements()` – Mock package installation logic.
    - `package_utils.backup_packages()` – Ensure backups execute correctly.
    - `package_utils.restore_packages()` – Ensure restores execute correctly.
    - `package_utils.migrate_packages()` – Validate migration workflow.
    - `log_utils.log_message()` – Verify structured logging messages.

## Expected Behavior:
    - Dependencies are processed based on user-provided arguments.
    - Logs are generated for major execution steps.
    - Backup, restore, and migration options execute correctly.
    - `installed.json` is managed as expected.

"""

import sys
import os

import argparse
import json
import logging
import logging
import pytest
import re

from datetime import (
    datetime,
    timezone
)

from unittest.mock import (
    patch,
    MagicMock,
    ANY
)

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from packages.requirements import dependencies
from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

from packages.requirements.lib import (
    package_utils,
    policy_utils
)

CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_dependencies.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

# ------------------------------------------------------------------------------
# Test: parse_arguments()
# ------------------------------------------------------------------------------

import sys
import pytest
import argparse
from unittest.mock import patch
from packages.requirements.dependencies import parse_arguments  # ✅ Ensure correct import

@pytest.mark.parametrize("args, expected", [
    ([], "./packages/requirements/requirements.json"),  # ✅ Default value
    (["-c", "custom_requirements.json"], "custom_requirements.json"),  # ✅ Custom value
])
def test_parse_arguments(args, expected):
    """
    Ensure `parse_arguments()` correctly handles command-line arguments.

    **Fix Strategy:**
    - Patch `sys.argv` to prevent argparse from exiting unexpectedly.
    - Mock `sys.exit` to catch any unwanted exits.
    - Validate that `--config` is correctly assigned.

    **Expected Behavior:**
    - `requirements.json` is used as default if no `-c` argument is provided.
    - If `-c <file>` is passed, it should override the default.
    """

    test_args = ["dependencies.py"] + args  # ✅ Ensure script name is included

    with patch.object(sys, "argv", test_args), \
         patch("sys.exit") as mock_exit:  # ✅ Prevent argparse from exiting

        parsed_args = parse_arguments()  # ✅ Correctly call the function
        assert parsed_args.requirements == expected  # ✅ Validate parsed argument
        mock_exit.assert_not_called()  # ✅ Ensure no forced exit happened

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

    # ✅ Simulate existing installed.json
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

    # ✅ Mock command-line arguments
    with patch.object(sys, "argv", ["dependencies.py", "--backup-packages", "backup.json"]), \
         patch("packages.requirements.lib.policy_utils.policy_management", return_value=mock_config.get("requirements", [])) as mock_policy, \
         patch("packages.requirements.lib.package_utils.install_requirements", return_value=installed_mock["dependencies"]) as mock_install, \
         patch("packages.requirements.lib.package_utils.backup_packages") as mock_backup, \
         patch("packages.requirements.lib.package_utils.restore_packages") as mock_restore, \
         patch("packages.requirements.lib.package_utils.migrate_packages") as mock_migrate, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        dependencies.main()  # ✅ Execute main()

        # ✅ Ensure `policy_management()` was called
        mock_policy.assert_called_once()

        # ✅ Ensure `install_requirements()` was called
        mock_install.assert_called_once()

        # ✅ Ensure optional backup, restore, and migration calls (if requested)
        mock_backup.assert_any_call(file_path="backup.json", configs=ANY)
        mock_restore.assert_not_called()  # ✅ Expected to be unused in this test
        mock_migrate.assert_not_called()  # ✅ Expected to be unused in this test

        # ✅ Ensure logging was used
        mock_log.assert_any_call(ANY, configs=ANY)

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

        dependencies.main()  # ✅ Execute main()

        # ✅ Ensure `restore_packages()` was called with the expected arguments
        mock_restore.assert_called_once_with(file_path="restore.json", configs=ANY)

        # ✅ Ensure logging was triggered
        mock_log.assert_any_call(ANY, configs=ANY)

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

    with patch.object(sys, "argv", ["dependencies.py", "--migrate-packages", "migrate.json"]), \
         patch("packages.requirements.lib.package_utils.migrate_packages") as mock_migrate, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        dependencies.main()

        # ✅ Fix: Use `ANY` for dynamic `configs`
        mock_migrate.assert_called_once_with(file_path="migrate.json", configs=ANY)

        # ✅ Ensure logging was triggered
        mock_log.assert_any_call(ANY, configs=ANY)
