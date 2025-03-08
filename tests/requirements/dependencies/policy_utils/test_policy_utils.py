#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/policy_utils/test_policy_utils.py
__version__ = "0.1.0"  ## Test Module version

"""
# PyTest Module: tests/requirements/dependencies/policy_utils/test_policy_utils.py

## Overview:
    This module contains unit tests for `policy_utils.py`, which is responsible for managing
    package installation policies. It ensures correct policy-based decisions such as:

    - **Installing missing packages**
    - **Upgrading outdated packages**
    - **Downgrading packages when required**
    - **Enforcing compliance with `installed.json`**

## Test Coverage:
    1. `policy_management(configs)`
       - Evaluates package policies based on installed and available versions.
       - Updates package statuses (`installing`, `upgrading`, `downgrading`, etc.).
       - Saves the evaluated requirements to `installed.json`.

    2. `installed_configfile(configs)`
       - Ensures correct retrieval of the `installed.json` path from configurations.

## Mocking Strategy:
    - `version_utils.installed_version()` → Simulates installed package versions.
    - `version_utils.latest_version()` → Simulates the latest available package versions.
    - `package_utils.installed_configfile()` → Mocks retrieval of `installed.json`.
    - `log_utils.log_message()` → Verifies that logs are generated correctly.

## Expected Behavior:
    - Dependencies are processed with the correct status updates.
    - `installed.json` is updated after policy evaluation.
    - Correct policy decisions are logged.

"""

import sys

import json
import logging
import pytest
import shutil
import subprocess

from unittest.mock import patch
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib import system_variables as environment

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

from packages.requirements.lib import (
    package_utils,
    policy_utils,
    version_utils
)

# Initialize CONFIGS
CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_policy_utils.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

# ------------------------------------------------------------------------------
# Test Setup: Mock Configs
# ------------------------------------------------------------------------------

@pytest.fixture
def mock_configs():
    """
    Creates a mock CONFIGS dictionary containing test dependencies.

    **Purpose:**
        - Simulates a dependency management environment.
        - Ensures `requirements.json` and `installed.json` structures are valid.
        - Prevents direct system modifications during test execution.

    ## Returns:
        - `dict`: A structured mock CONFIGS object with dependency configurations.
    """

    return {
        "packages": {
            "installation": {"configs": Path("/tmp/test_installed.json")}
        },
        "environment": {
            "INSTALL_METHOD": "pip", "EXTERNALLY_MANAGED": False
        },
        "logging": {
            "package_name": "requirements", "module_name": "policy_utils", "enable": False
        },
        "tracing": {"enable": False},
        "requirements": [
            {
                "package": "requests", "version": {
                    "policy": "latest", "target": "2.26.0", "latest": None, "status": None
                }
            },
            {
                "package": "numpy", "version": {
                    "policy": "latest", "target": "1.21.2", "latest": None, "status": None
                }
            }
        ]
    }

# ------------------------------------------------------------------------------
# Test: policy_management()
# ------------------------------------------------------------------------------

def test_policy_management(mock_configs):
    """
    Validate that `policy_management()` correctly applies package policies.

    **Test Strategy:**
        - Mocks `installed_version()` and `latest_version()` to simulate system state.
        - Ensures correct status assignment (`installing`, `upgrading`, `matched`, etc.).
        - Verifies that policy decisions are correctly logged.

    ## Mocking Details:
        - **Installed Versions:** `installed_version()` returns simulated package states.
        - **Available Versions:** `latest_version()` returns latest version from mock data.
        - **File Handling:** `installed_configfile()` is mocked to return `/tmp/test_installed.json`.

    ## Expected Behavior:
        - Dependencies are assigned correct statuses based on version comparison.
        - `[POLICY]` log messages are generated for each package decision.

    ## Assertions:
        - `requests` should be **marked as `matched`**.
        - `numpy` should be **marked as `installing`**.
    """

    temp_installed_file = mock_configs["packages"]["installation"]["configs"]

    installed_mock = {
        "dependencies": [
            {
                "package": "requests", "version": {
                    "policy": "latest", "target": "2.26.0", "latest": "2.26.0", "status": "latest"
                }
            },
            {
                "package": "numpy", "version": {
                    "policy": "latest", "target": "1.21.2", "latest": None, "status": "missing"
                }
            }
        ]
    }

    temp_installed_file.write_text(json.dumps(installed_mock, indent=4))

    with patch("packages.requirements.lib.version_utils.installed_version") as mock_installed, \
         patch("packages.requirements.lib.version_utils.latest_version") as mock_latest, \
         patch("packages.requirements.lib.package_utils.installed_configfile", return_value=temp_installed_file), \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        mock_installed.side_effect = ["2.26.0", None]  # requests installed, numpy missing
        mock_latest.side_effect = ["2.26.0", "1.21.2"]  # Latest available versions

        result = policy_utils.policy_management(mock_configs)

        # Validate package statuses
        assert result[0]["package"] == "requests"
        assert result[0]["version"]["status"] == "matched"

        assert result[1]["package"] == "numpy"
        assert result[1]["version"]["status"] == "installing"  # Should be marked for installation

        # Ensure `[POLICY]` log messages were generated
        mock_log.assert_any_call(
            '[POLICY]  Package "numpy" is missing. Installing latest.',
            configs=mock_configs
        )

# ------------------------------------------------------------------------------
# Test: installed_configfile()
# ------------------------------------------------------------------------------

def test_installed_configfile(mock_configs):
    """
    Ensure `installed_configfile()` returns the correct `installed.json` path.

    **Test Strategy:**
        - Uses `mock_configs` to simulate package installation settings.
        - Calls `installed_configfile()` to ensure correct file path retrieval.

    ## Expected Behavior:
        - The function should return the correct path to `installed.json`.
    """

    result = package_utils.installed_configfile(mock_configs)
    assert result == mock_configs["packages"]["installation"]["configs"]
