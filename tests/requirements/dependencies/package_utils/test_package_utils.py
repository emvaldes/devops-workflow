#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/package_utils/test_package_utils.py

__package__ = "requirements"
__module__ = "package_utils"

__version__ = "0.1.0"  ## Test Module version

"""
PyTest Module: tests/requirements/dependencies/package_utils/test_package_utils.py

This module contains unit tests for the `package_utils.py` submodule within `packages.requirements.lib`.

## Purpose:
    The `package_utils` module is responsible for **managing Python package dependencies** in a structured, policy-driven approach.
    These tests validate the correctness of package installation, backup, restoration, and compliance enforcement.

## Functional Scope:
    - **Backup & Restore Packages**:
      - Save and restore installed packages for migration or disaster recovery.
    - **Policy-Based Package Installation**:
      - Handle installation, upgrades, and downgrades based on predefined rules.
    - **Dependency Compliance Enforcement**:
      - Evaluate installed versions against required versions and enforce updates.
    - **Homebrew & Pip Integration**:
      - Use **Brew** if available, otherwise fallback to **Pip** with appropriate safeguards.
    - **Logging & Configuration Handling**:
      - Ensure structured logging and configuration retrieval.

## Test Coverage:
    The tests cover the following core functions:

    1. `backup_packages(file_path, configs)`**
       - Creates a backup of all installed Python packages.
       - Saves the package list in a requirements-compatible format.

    2. `install_package(package, version, configs)`**
       - Installs a package using **Brew (if applicable)** or **Pip**.
       - Ensures installation compliance with externally managed Python environments.

    3. `install_requirements(configs)`**
       - Processes dependency installations based on **predefined policies** (install, upgrade, downgrade, skip).
       - Integrates `review_packages()` to determine package compliance.

    4. `restore_packages(file_path, configs)`**
       - Reads a saved package list and reinstalls the packages.
       - Used for environment migrations or disaster recovery.

    5. `migrate_packages(file_path, configs)`**
       - Retrieves all installed packages and installs them in a new environment.
       - Useful when upgrading Python versions.

    6. `review_packages(configs)`**
       - Evaluates installed package versions against policy constraints.
       - Updates `installed.json` with package status details.

    7. `installed_configfile(configs)`**
       - Retrieves the configured path to `installed.json`.

## Testing Strategy:
    ### **Mocking Pip & Brew Calls**
        - Uses `unittest.mock.patch` to simulate **Pip & Homebrew** interactions.
        - Mocks `subprocess.run` for:
          - `pip freeze` (backup)
          - `pip install` (installation)
          - `brew install` (Homebrew-based installation)

    ### **Environment Handling**
        - Mocks `check_availability()` and `detect_environment()` to ensure the right **package manager** is selected.
        - Ensures **safe installation handling** for externally managed environments.
        - Prevents **unintended modifications** to system-managed Python distributions.

    ### **Version Enforcement**
        - Ensures that package compliance policies (`install`, `upgrade`, `downgrade`, `skip`) are **correctly applied**.
        - Uses `version_utils.installed_version()` to **retrieve currently installed versions**.
        - Mocks installed version retrieval to **simulate different package states** (`installed`, `outdated`, `missing`).

## Expected Outcomes:
    - **Packages are only installed when required**.
    - **Existing installations are preserved unless an update is necessary**.
    - **Logging captures relevant events** (`install`, `upgrade`, `downgrade`, `adhoc`).
    - **Policies are correctly enforced** (`install`, `upgrade`, `downgrade`, `skip`).
    - **Packages marked as `adhoc` are always installed**.
    - **Test environment remains unaffected by actual package modifications**.

"""

import sys
import json
import pytest
import subprocess

from unittest.mock import (
    ANY,
    patch,
    mock_open
)
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.mocks.config_loader import load_mock_requirements, load_mock_installed
from packages.requirements.lib import package_utils, policy_utils

# ------------------------------------------------------------------------------
# Test: backup_packages()
# ------------------------------------------------------------------------------

def test_backup_packages(requirements_config):
    """
    Validate that `backup_packages()` correctly saves the list of installed packages.

    **Mocked Components**:
        - `subprocess.run()` to simulate `pip freeze`.
        - `open()` to avoid writing to an actual file.
        - `log_utils.log_message()` to prevent dependency on `configs["logging"]`.

    **Expected Behavior**:
        - Ensures `pip freeze` runs correctly.
        - Writes package output to a file.
    """

    mock_file = mock_open()

    with patch("builtins.open", mock_file), \
         patch("subprocess.run") as mock_run, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:  # Mock log_message

        package_utils.backup_packages("test_backup.txt", requirements_config)

        # Ensure subprocess is correctly called to get package list
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "freeze"],
            stdout=mock_file.return_value,
            check=True
        )

        # Ensure file writing is correctly triggered
        mock_file.assert_called_with("test_backup.txt", "w")

        # Ensure logging was triggered (but no need for `configs["logging"]`)
        mock_log.assert_any_call(
            "[INFO] Installed packages list saved to test_backup.txt",
            "INFO",
            configs=requirements_config
        )

# ------------------------------------------------------------------------------
# Test: install_package()
# ------------------------------------------------------------------------------

def test_install_package_pip(requirements_config):
    """
    Ensure `install_package()` installs a package using Pip dynamically from `mock_requirements.json`.

    **Fix:**
        - Uses `requirements_config` to provide a structured config.
        - Mocks `subprocess.run` to avoid real installations.
        - Mocks `log_utils.log_message()` to prevent KeyError.
    """

    package_name = requirements_config["requirements"][0]["package"]  # Use correct key

    with patch("subprocess.run") as mock_run, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        package_utils.install_package(package_name, configs=requirements_config)

        # Ensure subprocess is correctly called to install package
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "install", "--quiet", "--user", package_name],
            check=False
        )

        # Ensure log_message was triggered with proper message
        mock_log.assert_any_call(
            f'[INSTALL] Installing "{package_name}" via Pip (default mode)...',
            "ERROR",
            configs=requirements_config
        )

# ------------------------------------------------------------------------------

def test_install_package_brew(installed_config):
    """
    Ensure `install_package()` installs a package using Homebrew dynamically from `mock_installed.json`.

    **Fix:**
        - Uses `installed_config` from `mock_installed.json` instead of `mock_requirements.json`.
        - Dynamically sets `"package_name"` and `"module_name"` in logging.
        - Mocks `brew_utils.check_availability()` to simulate Brew availability.
        - Mocks `subprocess.run` to prevent real package installations.
        - Mocks `log_message()` to prevent `KeyError`.
    """

    # Ensure the installed_config contains dependencies before proceeding
    assert len(installed_config["requirements"]) > 0, "ERROR: No packages found in mock_installed.json"

    package_name = installed_config["requirements"][0]["package"]

    with patch("subprocess.run") as mock_run, \
         patch("packages.requirements.lib.brew_utils.check_availability", return_value=True), \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        package_utils.install_package(
            package_name,
            configs={
                "environment": {"INSTALL_METHOD": "brew"},
                "logging": installed_config["logging"]
            }
        )

        # Print actual logs for debugging
        print("LOGGED MESSAGES:", mock_log.call_args_list)

        # Ensure `brew install` was called
        mock_run.assert_called_with(["brew", "install", package_name], check=False)

        # Normalize log messages for assertion
        logged_messages = [" ".join(str(call.args[0]).split()) for call in mock_log.call_args_list]

        # Ensure the expected message is present in any logged call
        expected_log = f"[INSTALL] Installing \"{package_name}\" via Homebrew..."
        assert any(expected_log in msg for msg in logged_messages), f"Expected log message '{expected_log}' not found in {logged_messages}"

# ------------------------------------------------------------------------------
# Test: install_requirements()
# ------------------------------------------------------------------------------

def test_install_requirements(requirements_config):
    """
    Ensure `install_requirements()` correctly installs dependencies based on `mock_requirements.json`.
    """

    with patch("packages.requirements.lib.package_utils.install_package") as mock_install:
        package_utils.install_requirements(requirements_config)

        for dep in requirements_config["requirements"]:
            mock_install.assert_any_call(dep["package"], None, requirements_config)

# ------------------------------------------------------------------------------

from unittest.mock import ANY

def test_install_requirements_adhoc(requirements_config):
    """
    Ensure `install_requirements()` correctly bypasses policy checks when `status="adhoc"`.
    """

    # Ensure config has the required key before modification
    assert "requirements" in requirements_config, "ERROR: Missing 'requirements' key in config."
    assert len(requirements_config["requirements"]) > 0, "ERROR: No dependencies found in requirements."

    # Modify `requirements_config` to force installation
    requirements_config["requirements"][0]["version"]["status"] = "adhoc"

    with patch("packages.requirements.lib.package_utils.install_package") as mock_install, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        # Execute package installation
        package_utils.install_requirements(requirements_config)

        # Extract log messages dynamically
        log_messages = [call.args[0] for call in mock_log.call_args_list]
        print("Captured Log Messages:", log_messages)

        # Search for expected patterns in logs (more flexible)
        expected_keywords = [
            "[AD-HOC] Forcing",
            "installation (bypassing policy checks)"
        ]
        assert any(
            all(keyword in message for keyword in expected_keywords)
            for message in log_messages
        ), "Expected '[AD-HOC]' log message not found!"

        # Ensure `install_package()` was called for **all** dependencies
        for dep in requirements_config["requirements"]:
            mock_install.assert_any_call(dep["package"], None, requirements_config)

# ------------------------------------------------------------------------------
# Test: restore_packages()
# ------------------------------------------------------------------------------

def test_restore_packages(requirements_config):
    """
    Ensure `restore_packages()` reinstalls packages from a backup file.
    """

    with patch("subprocess.run") as mock_run, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        # Use structured config instead of empty `{}`
        package_utils.restore_packages("test_backup.txt", requirements_config)

        # Ensure subprocess was called correctly
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "install", "--user", "-r", "test_backup.txt"],
            check=True
        )

        # Ensure log message was generated
        mock_log.assert_any_call(
            "[INFO] Installed packages restored successfully from test_backup.txt.",
            "INFO",
            configs=requirements_config
        )

# ------------------------------------------------------------------------------
# Test: review_packages()
# ------------------------------------------------------------------------------

def test_review_packages(installed_config):
    """
    Ensure `review_packages()` correctly evaluates installed package versions using `mock_installed.json`.
    """

    # Ensure the config has the correct key before accessing it
    assert "requirements" in installed_config, "ERROR: Missing 'requirements' key in installed_config."
    assert len(installed_config["requirements"]) > 0, "ERROR: No installed packages found in mock_installed.json."

    with patch("packages.requirements.lib.version_utils.installed_version") as mock_version:
        mock_version.side_effect = [dep["version"]["latest"] for dep in installed_config["requirements"]]

        result = package_utils.review_packages(installed_config)

        for i, dep in enumerate(installed_config["requirements"]):
            assert result[i]["package"] == dep["package"]
            assert result[i]["version"]["latest"] == dep["version"]["latest"]

# ------------------------------------------------------------------------------
# Test: installed_configfile()
# ------------------------------------------------------------------------------

def test_installed_configfile(installed_config):
    """
    Ensure `installed_configfile()` returns the correct `installed.json` path.
    """

    result = package_utils.installed_configfile(installed_config)
    assert result == installed_config["packages"]["installation"]["configs"]
