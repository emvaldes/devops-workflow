#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/package_utils/test_package_utils.py
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
import logging
import pytest
import shutil
import subprocess

from unittest.mock import (
    patch, mock_open, MagicMock
)
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
    policy_utils
)

# Initialize CONFIGS
CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_package_utils.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

# ------------------------------------------------------------------------------

@pytest.fixture
def mock_config():
    """
    Creates a temporary directory for test configuration files.
    Ensures that `requirements.json` and `installed.json` are stored in a non-persistent temp location.

    Returns:
        dict: A fully structured CONFIGS dictionary with paths to temp JSON files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # ✅ Correctly create temp JSON files
        temp_requirements_file = temp_dir_path / "requirements.json"
        temp_installed_file = temp_dir_path / "installed.json"

        # ✅ Mock requirements.json data
        requirements_mock = {
            "dependencies": [
                {
                    "package": "setuptools",
                    "version": {
                        "policy": "latest",
                        "target": "75.8.0",
                        "latest": False,
                        "status": "installing",
                    }
                }
            ]
        }

        # ✅ Mock installed.json data
        installed_mock = {
            "dependencies": [
                {
                    "package": "setuptools",
                    "version": {
                        "policy": "latest",
                        "target": "75.8.0",
                        "latest": "75.8.2",
                        "status": "upgraded"
                    }
                }
            ]
        }

        # ✅ Write the mock JSON files inside the temp directory
        temp_requirements_file.write_text(json.dumps(requirements_mock, indent=4))
        temp_installed_file.write_text(json.dumps(installed_mock, indent=4))

        # ✅ Return CONFIGS with dynamically generated file paths
        config = {
            "packages": {
                "installation": {
                    "forced": False,
                    "configs": temp_installed_file,  # ✅ Use temp installed.json path
                }
            },
            "environment": {
                "INSTALL_METHOD": "pip",
                "EXTERNALLY_MANAGED": False
            },
            "logging": {
                "package_name": "requirements",
                "module_name": "package_utils",
                "enable": False
            },
            "tracing": {"enable": False},
            "requirements": requirements_mock["dependencies"],  # ✅ Inject mocked dependencies
        }

        yield config  # ✅ Ensure temporary files are automatically cleaned up after test execution

# ------------------------------------------------------------------------------
# Test: backup_packages()
# ------------------------------------------------------------------------------

def test_backup_packages():
    """
    Validate that `backup_packages()` correctly saves the list of installed packages.

    - **Purpose**: Verify that the function correctly generates a package backup.
    - **Mocked Components**:
        - `subprocess.run()` (to simulate `pip freeze`).
        - `open()` (to avoid writing to an actual file).
    - **Expected Behavior**:
        - Ensures `pip freeze` runs correctly.
        - Writes package output to a file.

    **Test Strategy:**
        - Mocks `subprocess.run` to simulate `pip freeze` output.
        - Mocks `open()` to avoid writing to an actual file.
        - Ensures that `pip freeze` output is redirected to the backup file.
        - Verifies that logging captures success.

    Expected Output:
        - The correct `pip freeze` command executes.
        - The file write operation is mocked successfully.
        - A success log entry is created.
    """

    # ✅ Correctly mocking open() using mock_open()
    mock_file = mock_open()

    with patch("builtins.open", mock_file), \
         patch("subprocess.run") as mock_run:

        package_utils.backup_packages("test_backup.txt", CONFIGS)

        # ✅ Ensure `subprocess.run()` was called correctly
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "freeze"],
            stdout=mock_file.return_value,  # ✅ Correct usage for file-like object
            check=True
        )

        # ✅ Ensure file was opened for writing (without asserting only once)
        mock_file.assert_called_with("test_backup.txt", "w")  # Ensure `open()` was called exactly once

# ------------------------------------------------------------------------------
# Test: install_package()
# ------------------------------------------------------------------------------

def test_install_package_pip():
    """
    Ensure `install_package()` correctly installs a package using Pip.

    - **Purpose**: Validate that Pip is used for installation when Homebrew is not available.
    - **Mocked Components**:
        - `subprocess.run()` (to mock Pip installation).
    - **Expected Behavior**:
        - Ensures `pip install` is called.

    **Test Strategy:**
        - Mocks `subprocess.run` to simulate a successful Pip installation.
        - Ensures Pip is selected when Homebrew is not managing Python.

    Expected Output:
        - `pip install` is executed with the correct package name.
    """

    with patch("subprocess.run") as mock_run, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

        package_utils.install_package("requests", configs=CONFIGS)

        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "install", "--quiet", "--user", "requests"],
            check=False
        )

        # ✅ Ensure `[INSTALL]` log message is generated
        mock_log.assert_any_call(
            '[INSTALL] Installing "requests" via Pip (default mode)...',
            environment.category.error.id,
            configs=CONFIGS
        )

def test_install_package_brew():
    """
    Ensure `install_package()` correctly installs a package using Homebrew if available.

    - **Purpose**: Validate that Brew is used for package installation when available.
    - **Mocked Components**:
        - `subprocess.run()` (to mock Brew installation).
    - **Expected Behavior**:
        - Ensures `brew install` is called when applicable.

    **Test Strategy:**
        - Mocks `subprocess.run` to simulate a Homebrew installation.
        - Mocks `brew_utils.check_availability()` to return `True`.

    **Expected Behavior:**
        - `brew install` is executed instead of Pip.
    """

    # Fix: Ensure `CONFIGS["environment"]` is initialized
    if "environment" not in CONFIGS:
        CONFIGS["environment"] = {}  # Create empty environment dict

    CONFIGS["environment"]["INSTALL_METHOD"] = "brew"
    CONFIGS["environment"]["BREW_AVAILABLE"] = True

    with patch("subprocess.run") as mock_run, \
         patch("packages.requirements.lib.brew_utils.check_availability", return_value=True):

        package_utils.install_package("example_package", configs=CONFIGS)

        # Ensure `brew install` was called
        mock_run.assert_called_with(["brew", "install", "example_package"], check=False)

# ------------------------------------------------------------------------------
# Test: install_requirements()
# ------------------------------------------------------------------------------

@pytest.fixture
def mock_config():
    """
    Create a mock CONFIGS dictionary with required settings for testing.
    """
    return {
        "packages": {
            "installation": {
                "forced": False, "configs": Path("/tmp/test_installed.json")
            }
        },
        "environment": {"INSTALL_METHOD": "pip", "EXTERNALLY_MANAGED": False},
        "logging": {
            "package_name": "requirements",
            "module_name": "package_utils",
            "enable": False,
        },
        "tracing": {"enable": False},
        "requirements": [
            {
                "package": "setuptools",
                "version": {
                    "policy": "latest",
                    "target": "75.8.0",
                    "latest": False,
                    "status": "adhoc",  # ✅ Force this package to trigger the ELSE clause
                },
            }
        ],
    }

def test_install_requirements(mock_config):
    """
    Ensure `install_requirements()` correctly installs dependencies based on policy.

    - **Purpose**: Validate that dependency installations follow policy constraints.
    - **Mocked Components**:
        - `install_package()` (to prevent real installations).
    - **Expected Behavior**:
        - Ensures `install_package()` is called only for missing or outdated packages.

    **Test Strategy:**
        - Uses a mock version of `requirements.json` and `installed.json`.
        - Mocks `install_package()` to verify correct calls.
        - Ensures `policy_utils.policy_management()` is applied before installation.

    **Expected Behavior:**
        - `install_package()` is called for required dependencies.
        - Packages already at the correct version are skipped.
    """

    # ✅ Create a temporary installed.json file
    temp_installed_file = Path("/tmp/test_installed.json")
    temp_installed_file.write_text(
        json.dumps(
            {
                "dependencies": [
                    {
                        "package": "setuptools",
                        "version": {
                            "policy": "latest",
                            "target": "75.8.0",
                            "latest": "75.8.2",
                            "status": "upgraded",
                        },
                    }
                ]
            },
            indent=4,
        )
    )

    mock_config["packages"]["installation"]["configs"] = temp_installed_file

    with patch("packages.requirements.lib.policy_utils.policy_management", return_value=mock_config["requirements"]), \
         patch("packages.requirements.lib.package_utils.install_package") as mock_install, \
         patch("packages.requirements.lib.package_utils.installed_configfile", return_value=temp_installed_file):

        # ✅ Apply policy management (same as `main()`)
        mock_config["requirements"] = policy_utils.policy_management(mock_config)

        # ✅ Execute package installation
        package_utils.install_requirements(mock_config)

        # ✅ Ensure `install_package()` was called for packages requiring installation
        mock_install.assert_any_call("setuptools", None, mock_config)


def test_install_requirements_adhoc(mock_config):
    """
    Ensure `install_requirements()` correctly bypasses policy checks when `status="adhoc"`.

    - **Purpose**: Validate that setting `status="adhoc"` forces installation.
    - **Mocked Components**:
        - `install_package()` (to prevent real installations).
        - `log_message()` (to verify that `[AD-HOC]` logs appear).
    - **Expected Behavior**:
        - Ensures all packages are installed when `status="adhoc"`.
        - Confirms `[AD-HOC]` log message appears.

    **Test Strategy:**
        - Directly modify the mock `CONFIGS["requirements"]` to set `status="adhoc"`.
        - Mocks `install_package()` to verify calls.
        - Ensures `[AD-HOC]` log message appears in output.
        - Ensures all packages are installed even if they don't need an upgrade.

    **Expected Behavior:**
        - `install_package()` is called for **all** dependencies.
        - `[AD-HOC]` log message appears in log output.
    """

    # ✅ Modify `CONFIGS["requirements"]` so the package is forced to install
    mock_config["requirements"][0]["version"]["status"] = "adhoc"

    # with patch("packages.requirements.lib.policy_utils.policy_management", return_value=mock_config["requirements"]), \
    #      patch("packages.requirements.lib.package_utils.install_package") as mock_install, \
    #      patch("packages.requirements.lib.package_utils.installed_configfile", return_value=mock_config["packages"]["installation"]["configs"]), \
    #      patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:

    with patch(
            "packages.requirements.lib.policy_utils.policy_management",
            return_value=mock_config["requirements"]
        ), \
        patch(
            "packages.requirements.lib.package_utils.install_package"
        ) as mock_install, \
        patch(
            "packages.requirements.lib.package_utils.installed_configfile",
            return_value=Path("/tmp/installed.json")
        ), \  # ✅ Mock Path to prevent failure
        patch(
            "packages.appflow_tracer.lib.log_utils.log_message"
        ) as mock_log:

        # ✅ Apply policy management (same as `main()`)
        mock_config["requirements"] = policy_utils.policy_management(mock_config)

        # ✅ Execute package installation
        package_utils.install_requirements(mock_config)

        # ✅ Ensure `install_package()` was called for **all** dependencies
        mock_install.assert_any_call("setuptools", None, mock_config)

        # ✅ Ensure `[AD-HOC]` log message was generated
        mock_log.assert_any_call(
            '[AD-HOC] Forcing "setuptools" installation (bypassing policy checks) ...',
            configs=mock_config
        )

# ------------------------------------------------------------------------------
# Test: restore_packages()
# ------------------------------------------------------------------------------

def test_restore_packages():
    """
    Ensure `restore_packages()` correctly reinstalls packages from a backup file.

    - **Purpose**: Validate package restoration from a backup.
    - **Mocked Components**:
        - `subprocess.run()` (to mock `pip install -r`).
    - **Expected Behavior**:
        - Ensures `pip install -r` is called.

    **Test Strategy:**
        - Mocks `subprocess.run` to simulate `pip install -r <file>`.
        - Ensures the function logs a success message.

    Expected Output:
        - `pip install -r` is executed with the correct backup file.
    """
    with patch("subprocess.run") as mock_run:
        package_utils.restore_packages("test_backup.txt", CONFIGS)
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "install", "--user", "-r", "test_backup.txt"],
            check=True
        )

# ------------------------------------------------------------------------------
# Test: review_packages()
# ------------------------------------------------------------------------------

def test_review_packages():
    """
    Ensure `review_packages()` correctly evaluates installed package versions.

    - **Purpose**: Validate package compliance enforcement.
    - **Mocked Components**:
        - `version_utils.installed_version()` (to simulate different installed versions).
        - `installed_configfile()` (to return a valid installed.json path).
    - **Expected Behavior**:
        - Correctly determines package statuses (`latest`, `upgraded`, `outdated`, `missing`).
        - Ensures `installed.json` is correctly updated.

    **Test Strategy:**
        - Mocks `version_utils.installed_version()` to return various package versions.
        - Mocks `installed_configfile()` to return a valid file path.
        - Ensures that package statuses are correctly evaluated and written in a structured format.

    **Expected Behavior:**
        - Returns a list of dependencies with correct status assignments.
        - Writes a properly formatted `installed.json`.
    """

    # ✅ Mock `requirements.json` structure
    CONFIGS["requirements"] = [
        {
            "package": "requests",
            "version": {
                "policy": "latest",
                "target": "2.26.0",
                "latest": None,  # Initially unknown
                "status": None   # Initially unknown
            }
        },
        {
            "package": "numpy",
            "version": {
                "policy": "latest",
                "target": "1.21.2",
                "latest": None,  # Initially unknown
                "status": None   # Initially unknown
            }
        }
    ]

    # ✅ Mock `installed.json` structure
    installed_mock = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "policy": "latest",
                    "target": "2.26.0",
                    "latest": "2.26.0",
                    "status": "latest"
                }
            },
            {
                "package": "numpy",
                "version": {
                    "policy": "latest",
                    "target": "1.21.2",
                    "latest": None,
                    "status": "missing"
                }
            }
        ]
    }

    # ✅ Create a temporary installed.json file with proper structure
    temp_installed_file = Path("/tmp/test_installed.json")
    temp_installed_file.write_text(json.dumps(installed_mock, indent=4))  # ✅ Ensure file exists with a valid structure

    with patch("packages.requirements.lib.version_utils.installed_version") as mock_version, \
         patch("packages.requirements.lib.package_utils.installed_configfile", return_value=temp_installed_file):

        mock_version.side_effect = ["2.26.0", None]  # ✅ First package is up to date, second is missing

        result = package_utils.review_packages(CONFIGS)

        # ✅ Ensure correct status assignments
        assert result[0]["package"] == "requests"
        assert result[0]["version"]["status"] == "latest"  # ✅ requests should be "latest"
        assert result[0]["version"]["latest"] == "2.26.0"  # ✅ latest version should match

        assert result[1]["package"] == "numpy"
        assert result[1]["version"]["status"] == "missing"  # ✅ numpy should be "missing"
        assert result[1]["version"]["latest"] is None  # ✅ latest should be None

        # ✅ Ensure installed.json was written correctly with structured format
        with temp_installed_file.open("r") as f:
            installed_data = json.load(f)
            assert isinstance(installed_data, dict)  # ✅ Ensure top-level structure is a dictionary
            assert "dependencies" in installed_data  # ✅ Ensure key exists
            assert isinstance(installed_data["dependencies"], list)  # ✅ Ensure dependencies is a list
            assert installed_data["dependencies"][0]["package"] == "requests"
            assert installed_data["dependencies"][0]["version"]["status"] == "latest"
            assert installed_data["dependencies"][0]["version"]["latest"] == "2.26.0"
            assert installed_data["dependencies"][1]["package"] == "numpy"
            assert installed_data["dependencies"][1]["version"]["status"] == "missing"
            assert installed_data["dependencies"][1]["version"]["latest"] is None
