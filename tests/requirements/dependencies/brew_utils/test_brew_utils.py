#!/usr/bin/env python3

# File: ./tests/appflow_tracer/brew_utils/brew_utils.py

__package_name__ = "requirements"
__module_name__ = "brew_utils"

__version__ = "0.1.0"  ## Package version

"""
# PyTest Module: `tests/requirements/dependencies/brew_utils/test_brew_utils.py`

## **Purpose**
    This module contains unit tests for the `brew_utils.py` submodule, which is responsible for detecting and interacting with **Homebrew**, a package manager primarily used on macOS.

These tests validate:
    - **Detection of Homebrew** (`check_availability()`)
    - **Python environment identification** (`detect_environment()`)
    - **Version retrieval for installed Homebrew packages** (`version()`)
    - **Retrieval of the latest available package version** (`latest_version()`)

---

## **Test Strategy**
### 1️⃣ **Mocking Homebrew Calls**
    - Uses `unittest.mock.patch` to simulate CLI commands (`brew list`, `brew info`) without modifying the system.
    - Mocks `subprocess.run()` to ensure system calls execute **without** real installations or queries.
    - Mocks `shutil.which()` to simulate whether Homebrew is installed.

### 2️⃣ **Environment Detection**
    - Ensures `detect_environment()` correctly identifies:
      - **Homebrew-based Python installations**
      - **System-managed Python installations**
      - **Standalone Python installations**
    - Mocks `check_availability()` to return different system states.

### 3️⃣ **Validating Installed & Available Versions**
    - Ensures **correct retrieval** of:
      - Installed package versions (`version()`)
      - The latest available package versions (`latest_version()`)
    - Uses **mocked JSON data** from `mock_requirements.json` & `mock_installed.json` to provide **configurable test cases**.

---

## **Test Coverage**
| Function Name            | Purpose                                         | Expected Outcome |
|--------------------------|-------------------------------------------------|------------------|
| `check_availability()`   | Determines if Homebrew is installed.            | `True` or `False` |
| `detect_environment()`   | Identifies Python installation method.          | `brew`, `system`, or `standalone` |
| `version(package)`       | Retrieves installed version of a package.       | Installed version (`str`) or `None` |
| `latest_version(package)`| Retrieves latest available package version.     | Latest version (`str`) or `None` |

---
## **Mock Data Sources**
    - **`tests/mocks/mock_requirements.json`** → Defines **expected** package configurations (policies).
    - **`tests/mocks/mock_installed.json`** → Defines **actual** installed package states (real-world scenario).

---
## **Expected Behavior**
    - **Homebrew detection is accurate**
    - **Installed package versions are correctly retrieved**
    - **Latest versions are fetched correctly**
    - **System environment is identified correctly**
    - **Tests are isolated from actual Homebrew installations**
"""

import sys

import pytest
import subprocess

from unittest.mock import patch

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib import system_variables as environment

from packages.appflow_tracer.lib import log_utils
from packages.requirements.lib import brew_utils

# ✅ Skip the entire test suite if Homebrew is unavailable
pytestmark = pytest.mark.skipif(
    not brew_utils.check_availability(),
    reason="Homebrew is not available on this system."
)

# -----------------------------------------------------------------------------
# Test: check_availability()
# -----------------------------------------------------------------------------

@pytest.mark.skipif(not brew_utils.check_availability(), reason="Homebrew is not available on this system.")
def test_check_availability_success():
    """
    ✅ **Test: Homebrew Availability (Success)**

    **Purpose:**
    - Verify that `check_availability()` correctly detects when Homebrew is installed.

    **Test Strategy:**
    - **Mock `shutil.which()`** to return a valid `brew` path.
    - **Mock `subprocess.run()`** to simulate a successful `brew --version` command.

    **Expected Outcome:**
    - Returns `True` when Homebrew is detected.

    **Scenario:**
    - Homebrew is installed and accessible via `/usr/local/bin/brew`.
    """

    with patch("shutil.which", return_value="/usr/local/bin/brew"), \
         patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0)):
        assert brew_utils.check_availability() is True

# -----------------------------------------------------------------------------

def test_check_availability_failure():
    """
    ❌ **Test: Homebrew Availability (Failure)**

    **Purpose:**
    - Ensure `check_availability()` correctly identifies when Homebrew is **not installed**.

    **Test Strategy:**
    - **Clear `lru_cache`** before execution to ensure fresh results.
    - **Mock `shutil.which()`** to return `None`, simulating a missing Homebrew installation.

    **Expected Outcome:**
    - Returns `False` when Homebrew is **not detected**.

    **Scenario:**
    - Homebrew is **not installed** or its binary is not in the system `PATH`.
    """

    brew_utils.check_availability.cache_clear()  # ✅ Clear cache BEFORE calling the function.

    with patch("shutil.which", return_value=None):
        result = brew_utils.check_availability()
        assert result is False  # ✅ Expect False if Homebrew is missing

# -----------------------------------------------------------------------------

def test_brew_package_not_found():
    """
    Ensure `brew_info()` correctly handles non-existent packages.

    **Test Strategy:**
        - Mocks `subprocess.run` to simulate `brew info` failing.

    Expected Output:
        - `None` when the package is not found.
    """

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stderr = "Error: No formula found"
        # ✅ Ensure the correct function name is used
        result = brew_utils.brew_info("nonexistent_package")
        assert result is None  # ✅ Expect `None` for missing packages

# -----------------------------------------------------------------------------
# Test: detect_environment()
# -----------------------------------------------------------------------------

def test_detect_environment_brew():
    """
    ✅ **Test: Detect Homebrew-Managed Python Environment**

    **Purpose:**
    - Validate that `detect_environment()` correctly identifies a **Homebrew-managed Python installation**.

    **Test Strategy:**
    - **Mock `check_availability()`** to return `True`, indicating Homebrew is installed.
    - **Mock `subprocess.run()`** to simulate successful execution of `brew --prefix python`.

    **Expected Outcome:**
    - `INSTALL_METHOD`: `"brew"`
    - `BREW_AVAILABLE`: `True`

    **Scenario:**
    - The system has Homebrew installed and Python is managed by Homebrew.
    """

    with patch("packages.requirements.lib.brew_utils.check_availability", return_value=True), \
         patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0)):
        env = brew_utils.detect_environment()
        assert env["INSTALL_METHOD"] == "brew"
        assert env["BREW_AVAILABLE"] is True

# -----------------------------------------------------------------------------

def test_detect_environment_standalone():
    """
    ❌ **Test: Detect Standalone Python Environment**

    **Purpose:**
    - Ensure `detect_environment()` correctly identifies when Python is **not managed by Homebrew**.

    **Test Strategy:**
    - **Mock `check_availability()`** to return `False`, indicating Homebrew is missing.

    **Expected Outcome:**
    - `INSTALL_METHOD`: `"standalone"` or `"system"`
    - `BREW_AVAILABLE`: `False`

    **Scenario:**
    - The system runs Python from system package managers (`apt`, `dnf`) or standalone installations.
    """

    with patch("packages.requirements.lib.brew_utils.check_availability", return_value=False):
        env = brew_utils.detect_environment()
        assert env["INSTALL_METHOD"] in ["standalone", "system"]
        assert env["BREW_AVAILABLE"] is False  # ✅ Confirm Homebrew is unavailable

# -----------------------------------------------------------------------------
# Test: version(package)
# -----------------------------------------------------------------------------

def test_version_installed(requirements_config):
    """
    ✅ **Test: Retrieve Installed Package Version (Homebrew)**

    **Purpose:**
    - Validate that `version(package)` correctly retrieves the installed version of a Homebrew-managed package.

    **Test Strategy:**
    - Use **mocked package name** from `mock_requirements.json`.
    - **Mock `subprocess.run()`** to return a valid `brew list --versions` output.

    **Expected Outcome:**
    - Returns the installed version (e.g., `"1.6.10"`).

    **Scenario:**
    - The package exists and is installed via Homebrew.
    """

    # ✅ Use the correct key: "requirements" instead of "dependencies"
    package_name = requirements_config["requirements"][0]["package"]
    expected_version = requirements_config["requirements"][0]["version"]["target"]

    with patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=f"{package_name} {expected_version}")):
        assert brew_utils.version(package_name) == expected_version

# -----------------------------------------------------------------------------

def test_version_not_installed():
    """
    ❌ **Test: Handle Missing Package in Homebrew**

    **Purpose:**
    - Ensure `version(package)` returns `None` when the package is not installed.

    **Test Strategy:**
    - **Mock `subprocess.run()`** to raise `subprocess.CalledProcessError`, simulating a missing package.

    **Expected Outcome:**
    - Returns `None` for non-existent packages.

    **Scenario:**
    - The package **is not installed** in Homebrew.
    """

    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "brew")):
        assert brew_utils.version("nonexistent-package") is None

# -----------------------------------------------------------------------------
# Test: latest_version(package)
# -----------------------------------------------------------------------------

def test_latest_version_success(installed_config):
    """
    ✅ **Test: Retrieve Latest Available Version of a Homebrew Package**

    **Purpose:**
    - Validate that `latest_version(package)` correctly extracts the latest stable version of a Homebrew package.

    **Test Strategy:**
    - Use **mocked package name & version** from `mock_installed.json`.
    - **Mock `subprocess.run()`** to return valid `brew info` output.

    **Expected Outcome:**
    - Returns the latest version (e.g., `"8.3.5"`).

    **Scenario:**
    - The package is available in Homebrew and has a newer version.
    """

    # ✅ Use the correct key: "requirements" instead of "dependencies"
    package_name = installed_config["requirements"][0]["package"]
    latest_version = installed_config["requirements"][0]["version"]["latest"]

    # Ensure latest_version is valid before proceeding
    assert latest_version and isinstance(latest_version, str), f"Invalid latest_version value: {latest_version}"

    brew_output = f"""{package_name}: stable {latest_version} (bottled)
https://formulae.brew.sh/formula/{package_name}"""

    with patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=brew_output)):
        assert brew_utils.latest_version(package_name) == latest_version

# -----------------------------------------------------------------------------

def test_latest_version_failure():
    """
    Ensure `latest_version()` returns `None` when the package does not exist in Homebrew.

    **Test Strategy:**
        - Mocks `subprocess.run` to raise `subprocess.CalledProcessError`.

    Expected Output:
        - `None` when the package is not found.
    """

    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "brew")):
        assert brew_utils.latest_version("nonexistent-package") is None
