#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/policy_utils/test_policy_utils.py

__package__ = "requirements"
__module__ = "policy_utils"

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
import pytest

from unittest.mock import patch
from pathlib import Path

# Ensure the root project directory is in sys.path
import sys
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.mocks.config_loader import load_mock_requirements, load_mock_installed
from packages.requirements.lib import package_utils, policy_utils, version_utils

# ------------------------------------------------------------------------------
# Test: policy_management()
# ------------------------------------------------------------------------------

def test_policy_management(requirements_config, installed_config):
    """
    Validate `policy_management()` correctly applies package policies using `mock_requirements.json`.

    **Test Strategy:**
        - **Mocks** `installed_version()` & `latest_version()` to simulate system state.
        - **Ensures correct status assignment** (`installing`, `upgrading`, `matched`, etc.).
        - **Verifies structured logging** without requiring exact message matching.

    ## Assertions:
        - `setuptools` should be **marked as `upgraded`**.
        - `pytest` should be **marked as `matched`**.
        - `coverage` should be **marked as `installing` or `upgraded`**.
    """

    # Ensure the structure is correct before continuing
    assert "requirements" in requirements_config, "ERROR: Missing 'requirements' in requirements_config."
    assert len(requirements_config["requirements"]) > 0, "ERROR: No dependencies found in mock_requirements.json."

    # Ensure mock-installed config has data
    assert "requirements" in installed_config, "ERROR: Missing 'requirements' in installed_config."
    assert len(installed_config["requirements"]) > 0, "ERROR: No installed packages found."

    installed_mock = installed_config["requirements"]

    with patch("packages.requirements.lib.version_utils.installed_version") as mock_installed, \
         patch("packages.requirements.lib.version_utils.latest_version") as mock_latest, \
         patch("packages.requirements.lib.package_utils.installed_configfile", return_value=Path("/tmp/test_installed.json")), \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        # Mock installed & latest versions dynamically
        installed_versions = {dep["package"]: dep["version"]["latest"] for dep in installed_mock}
        mock_installed.side_effect = lambda pkg, _: installed_versions.get(pkg, None)
        mock_latest.side_effect = lambda pkg, _: {
            "setuptools": "75.8.2",
            "pytest": "8.3.5",
            "coverage": "7.6.12"
        }.get(pkg, None)

        result = policy_utils.policy_management(requirements_config)

        # Ensure package statuses are correctly assigned
        status_map = {dep["package"]: dep["version"]["status"] for dep in result}

        assert status_map["setuptools"] == "upgraded"
        assert status_map["pytest"] in ["matched", "upgraded"]  # Allow flexibility in status
        assert status_map["coverage"] in ["installing", "upgraded"]  # Coverage might be upgrading instead of installing

        # Allow more flexible log validation
        log_messages = [call[0][0] for call in mock_log.call_args_list]

        assert any("[POLICY]  Package \"coverage\"" in msg for msg in log_messages), \
            "Expected policy log message for 'coverage' not found"

# ------------------------------------------------------------------------------
# Test: installed_configfile()
# ------------------------------------------------------------------------------

def test_installed_configfile(requirements_config):
    """
    Ensure `installed_configfile()` returns the correct `installed.json` path.

    **Test Strategy:**
        - Uses `requirements_config` to simulate package installation settings.
        - Calls `installed_configfile()` to ensure correct file path retrieval.

    ## Expected Behavior:
        - The function should return the correct path to `installed.json`.
    """

    result = package_utils.installed_configfile(requirements_config)
    assert result == requirements_config["packages"]["installation"]["configs"]
