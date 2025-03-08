#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/version_utils/test_version_utils.py
__version__ = "0.1.0"  ## Test Module version

"""
# Pytest Module: tests/requirements/dependencies/version_utils/test_version_utils.py

## Overview:
This module contains unit tests for `version_utils.py`, which is responsible for retrieving
installed and latest package versions from various sources, including:

- **Pip (`pip list`, `pip index versions`)**
- **Homebrew (`brew info`, `brew list`)**
- **APT/DNF (`dpkg -s`, `apt-cache`, `dnf list available`)**
- **Windows Package Manager (`Get-AppxPackage`, `Find-Package`)**

## Test Coverage:
1. `installed_version(package, configs)`
   - Retrieves the installed package version using Pip, Brew, APT, or Windows Store.
   - Ensures **multi-platform support**.

2. `latest_version(package, configs)`
   - Fetches the latest available version of a package from the appropriate source.

3. `pip_latest_version(package)`
   - Uses `pip index versions` to fetch the latest available package version.

4. `linux_version(package)`
   - Retrieves the installed version of a package via **APT/DNF**.

5. `linux_latest_version(package)`
   - Queries the latest available version of a package via **APT/DNF**.

6. `windows_version(package)`
   - Retrieves the installed package version via **Windows Package Manager**.

7. `windows_latest_version(package)`
   - Fetches the latest available version of a package from **Windows Package Manager**.

## Mocking Strategy:
- **Pip Commands (`pip list`, `pip index versions`)** – Mocked using `subprocess.run`.
- **Homebrew (`brew list`, `brew info`)** – Simulated package version responses.
- **APT/DNF (`dpkg -s`, `apt-cache`)** – Mocked Linux package manager queries.
- **Windows Package Manager (`powershell Get-AppxPackage`)** – Mocked Windows queries.

## Expected Behavior:
- Correctly retrieves installed versions across multiple platforms.
- Accurately fetches the latest package versions when available.
- Returns `None` when a package is not found.
"""

import sys
import json
import logging
import pytest
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
    logname_override='logs/tests/test_version_utils.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

# ------------------------------------------------------------------------------
# Test: installed_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, installed_version", [
    ("requests", "2.26.0"),
    ("numpy", None),  # Simulate package not installed
])
def test_installed_version(package, installed_version):
    """
    Ensure `installed_version()` correctly retrieves the installed package version.

    **Test Strategy:**
        - Mocks `pip list --format=json` to simulate installed packages.
        - Ensures correct version retrieval from Pip.
        - Ensures `None` is returned if the package is not installed.

    ## Args:
        - `package` (`str`): The package name being tested.
        - `installed_version` (`Optional[str]`): The expected installed version or `None` if the package is missing.

    ## Expected Behavior:
        - Returns the correct installed version if the package exists.
        - Returns `None` if the package is not installed.
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
        mock_metadata.side_effect = lambda pkg: {"requests": "2.26.0", "pandas": "1.4.2"}.get(pkg.lower(), None)

        result = version_utils.installed_version(package, CONFIGS)

        if installed_version is None:
            assert result is None  # ✅ Ensure missing package returns None
        else:
            assert result == installed_version  # ✅ Ensure correct version is returned

# ------------------------------------------------------------------------------
# Test: latest_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, latest_version", [
    ("requests", "2.28.0"),
    ("numpy", "1.23.4"),
])
def test_latest_version(package, latest_version):
    """
    Ensure `latest_version()` correctly fetches the latest available package version.

    **Test Strategy:**
        - Mocks `pip index versions <package>` to simulate the latest version retrieval.
        - Ensures correct version extraction from Pip.
    """

    mock_pip_versions = f"Available versions: {latest_version}, 1.21.2, 1.18.5"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_pip_versions

        result = version_utils.latest_version(package, CONFIGS)
        assert result == latest_version

# ------------------------------------------------------------------------------
# Test: linux_version()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("package, installed_version", [
    ("curl", "7.68.0"),  # ✅ Simulate installed package
    ("vim", None),  # ✅ Simulate missing package
])
def test_linux_version(package, installed_version):
    """
    Ensure `linux_version()` correctly retrieves installed package versions via APT or DNF.

    **Test Strategy:**
        - Mocks `dpkg -s <package>` to simulate package installation status.
        - Ensures correct version retrieval or `None` if package is missing.
    """

    # ✅ Mock output for installed package
    mock_dpkg_output = f"Package: {package}\nVersion: 7.68.0"

    with patch("subprocess.run") as mock_run:
        if installed_version is not None:
            # ✅ Simulate package found via dpkg
            mock_run.return_value.stdout = mock_dpkg_output
        else:
            # ✅ Simulate package NOT found (dpkg should fail)
            mock_run.side_effect = subprocess.CalledProcessError(1, "dpkg")

        result = version_utils.linux_version(package)

        # ✅ Ensure correct behavior for installed & missing packages
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

    **Test Strategy:**
        - Mocks `powershell Get-AppxPackage -Name <package>` command output.
        - Ensures correct version retrieval or `None` if package is missing.
    """

    # ✅ Simulate correct PowerShell behavior
    mock_powershell_output = (
        "1.5.00.33362" if package == "MicrosoftTeams" else ""  # Return empty string for missing package
    )

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_powershell_output

        result = version_utils.windows_version(package)

        if installed_version is None:
            assert result is None  # ✅ Ensure missing package returns None
        else:
            assert result == installed_version  # ✅ Ensure correct version is returned

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
        assert result == latest_version
