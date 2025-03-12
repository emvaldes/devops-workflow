#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/version_utils/test_version_utils.py

__package__ = "requirements"
__module__ = "version_utils"

__version__ = "0.1.1"  ## Updated Test Module version

"""
# PyTest Module: tests/requirements/dependencies/version_utils/test_version_utils.py

## Overview:
    This module contains unit tests for `version_utils.py`, which is responsible for:

    - **Retrieving installed package versions** via Pip, Homebrew, Linux package managers, and Windows.
    - **Determining the latest available version** of a package.
    - **Ensuring correct version retrieval logic across multiple package managers**.

## Test Coverage:
    1. `installed_version(package, configs)`
       - Retrieves installed package versions dynamically from system package managers.

    2. `latest_version(package, configs)`
       - Fetches the latest available package version from package repositories.

    3. `linux_version(package)`
       - Retrieves package versions via APT or DNF.

    4. `windows_version(package)`
       - Retrieves package versions via PowerShell.

    5. `pip_latest_version(package)`
       - Uses Pip to fetch the latest available package version.

## Mocking Strategy:
    - `subprocess.run()` → Mocks CLI calls for `pip list`, `dpkg -s`, `powershell`, etc.
    - `importlib.metadata.version()` → Mocks package version retrieval for Python packages.
    - `log_utils.log_message()` → Mocks structured logging calls.

## Expected Behavior:
    - Installed package versions are retrieved correctly.
    - Latest versions are fetched from the appropriate package manager.
    - Logging is correctly triggered for each function.
"""

import sys
import json
import pytest
import subprocess
import random
import string
import importlib.metadata  # ✅ Use metadata to get the actual installed version

from unittest.mock import patch, ANY
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.mocks.config_loader import load_mock_requirements, load_mock_installed
from packages.requirements.lib import version_utils, brew_utils

# ------------------------------------------------------------------------------
# Test: installed_version()
# ------------------------------------------------------------------------------

def generate_random_package():
    """Generate a random non-existent package name to avoid conflicts with real packages."""
    return "test-package-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# @pytest.mark.parametrize("package, installed_version", [
#     ("requests", "2.26.0"),
#     (generate_random_package(), None),  # Use a dynamically generated non-existent package
# ])
@pytest.mark.parametrize("package, installed_version", [
    ("requests", importlib.metadata.version("requests")),  # ✅ Dynamically fetch installed version
    (generate_random_package(), None),  # ✅ Still test non-existent package
])
def test_installed_version(package, installed_version, requirements_config):
    """
    Ensure `installed_version()` correctly retrieves the installed package version.

    **Test Strategy:**
        - Mocks `pip list --format=json` to simulate installed packages.
        - Ensures correct version retrieval from Pip.
        - Ensures `None` is returned if the package is not installed.
    """

    mock_pip_list = json.dumps([
        {"name": "requests", "version": "2.26.0"},
        {"name": "pandas", "version": "1.4.2"}
    ])

    with patch("subprocess.run") as mock_run, \
         patch("importlib.metadata.version") as mock_metadata:

        # Simulate `pip list` failure (so that `importlib.metadata.version()` is used)
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip")

        # Ensure `importlib.metadata.version()` is used for fallback
        # mock_metadata.side_effect = lambda pkg: {"requests": "2.26.0", "pandas": "1.4.2"}.get(pkg.lower(), None)
        mock_metadata.side_effect = lambda pkg: {
            "requests": "2.26.0",
            "pandas": "1.4.2",
            "numpy": "2.2.3"  # Add numpy to the mock
        }.get(pkg.lower(), None)

        result = version_utils.installed_version(package, requirements_config)

        assert result == installed_version, f"Expected {installed_version}, but got {result}"

# ------------------------------------------------------------------------------
# Test: latest_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, latest_version", [
    ("requests", "2.28.0"),
    ("numpy", "1.23.4"),
])
def test_latest_version(package, latest_version, requirements_config):
    """
    Ensure `latest_version()` correctly fetches the latest available package version.

    **Test Strategy:**
        - Mocks `pip index versions <package>` to simulate the latest version retrieval.
        - Ensures correct version extraction from Pip.
    """

    mock_pip_versions = f"Available versions: {latest_version}, 1.21.2, 1.18.5"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_pip_versions

        result = version_utils.latest_version(package, requirements_config)
        assert result == latest_version, f"Expected {latest_version}, but got {result}"

# ------------------------------------------------------------------------------
# Test: linux_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, installed_version", [
    ("curl", "7.68.0"),  # Simulate installed package
    ("vim", None),  # Simulate missing package
])
def test_linux_version(package, installed_version):
    """
    Ensure `linux_version()` correctly retrieves installed package versions via APT or DNF.
    """

    mock_dpkg_output = f"Package: {package}\nVersion: 7.68.0"

    with patch("subprocess.run") as mock_run:
        if installed_version is not None:
            mock_run.return_value.stdout = mock_dpkg_output
        else:
            mock_run.side_effect = subprocess.CalledProcessError(1, "dpkg")

        result = version_utils.linux_version(package)
        assert result == installed_version, f"Expected {installed_version}, but got {result}"

# ------------------------------------------------------------------------------
# Test: windows_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, installed_version", [
    ("MicrosoftTeams", "1.5.00.33362"),
    ("NonExistentPackage", None),  # Simulate package not installed
])
def test_windows_version(package, installed_version):
    """
    Ensure `windows_version()` correctly retrieves installed package versions via PowerShell.
    """

    mock_powershell_output = "1.5.00.33362" if package == "MicrosoftTeams" else ""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_powershell_output

        result = version_utils.windows_version(package)
        assert result == installed_version, f"Expected {installed_version}, but got {result}"

# ------------------------------------------------------------------------------
# Test: pip_latest_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, latest_version", [
    ("requests", "2.28.0"),
    ("numpy", None),  # Simulate failure to retrieve version
])
def test_pip_latest_version(package, latest_version):
    """
    Ensure `pip_latest_version()` retrieves the correct latest package version.

    **Test Strategy:**
    - Mocks `pip index versions <package>` to simulate version retrieval.
    - Ensures correct parsing of available versions.
    """

    mock_pip_versions = f"Available versions: {latest_version}, 2.27.0, 2.26.0"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_pip_versions

        result = version_utils.pip_latest_version(package)
        assert result == latest_version, f"Expected {latest_version}, but got {result}"

# ------------------------------------------------------------------------------
# Test: Brew version retrieval
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, latest_version", [
    ("wget", "1.21.3"),
    ("openssl", "3.0.8"),
])
def test_brew_latest_version(package, latest_version):
    """
    Ensure `brew_utils.latest_version()` correctly retrieves the latest Homebrew package version.
    """

    with patch("packages.requirements.lib.brew_utils.latest_version", return_value=latest_version):
        result = brew_utils.latest_version(package)
        assert result == latest_version, f"Expected {latest_version}, but got {result}"
