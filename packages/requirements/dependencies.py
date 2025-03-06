#!/usr/bin/env python3

# File: ./packages/requirements/dependencies.py
__version__ = "0.1.0"  ## Package version

"""
File Path: packages/appflow_tracer/tracing.py

Description:
    **AppFlow Tracer - Advanced Dependency Management System**

    This module provides a structured and policy-driven approach to managing
    dependencies across various environments. It supports both **Homebrew (macOS)**
    and **Pip (cross-platform)** while ensuring compliance with package versioning policies.
    The module dynamically detects the Python installation method and adapts its
    installation strategy based on whether the system is **externally managed**.

Core Features:
    - **Environment Detection**: Determines if Python is installed via Homebrew, system package managers (APT/DNF), or standalone.
    - **Brew & Pip Integration**: Uses Brew when appropriate; otherwise, prioritizes Pip installations with safe handling.
    - **Safe Installation Policies**:
      - Uses `--user` for Pip installations when applicable.
      - Respects externally managed environments and prevents breaking system packages unless explicitly allowed (`--force`).
      - Falls back to manual instructions if `--force` is not set in externally managed environments.
    - **Dependency Installation & Verification**:
      - Installs missing packages based on a structured JSON file.
      - Verifies installed versions against required versions.
      - Updates, upgrades, or downgrades packages based on predefined policies.
    - **Logging & Debugging**:
      - Logs all package operations, warnings, and errors.
      - Provides clear debugging information about installation attempts and failures.
    - **Package Status Reporting**:
      - Displays installed packages with version and compliance details.
      - Writes package installation results into `installed.json`.

Usage:
    - **Install or Update Dependencies**:
        ```python
        from tracing import install_requirements
        install_requirements(configs=configs)
        ```
    - **Show Installed Packages**:
        ```bash
        python tracing.py --show-installed
        ```
    - **Force Install in an Externally Managed Environment**:
        ```bash
        python tracing.py -f
        ```

Dependencies:
    - `subprocess` - For running Brew and Pip commands.
    - `argparse` - For parsing command-line arguments.
    - `json` - For handling requirements JSON files.
    - `importlib.metadata` - For fetching installed package versions.
    - `pathlib` - For safe file path handling.
    - `datetime` - For logging timestamps.
    - `functools.lru_cache` - For caching frequently accessed data.
    - `lib.system_variables` - Handles project-wide configurations.
    - `lib.log_utils` - Provides structured logging.

Global Variables:
    - `CONFIGS`: Stores runtime configurations, logging, and installation settings.
    - `LIB_DIR`: Directory path for the `lib` directory.
    - `BREW_AVAILABLE`: Boolean indicating whether Homebrew is available.
    - `installed.json`: Stores the installed package states.

Primary Functions:
    - **Environment & Dependency Management**:
        - `check_brew_availability()`: Detects if Brew is installed on macOS.
        - `detect_python_environment(brew_available)`: Identifies Python installation method and package management constraints.
        - `installed_version(package, configs)`: Returns the installed version of a package.
        - `latest_version(package, configs)`: Fetches the latest available version of a package.

    - **Package Installation & Handling**:
        - `package_management(package, version, configs)`: Installs a package using Brew (if appropriate) or Pip with safe policies.
        - `install_requirements(configs)`: Installs/upgrades/downgrades dependencies based on `policy_management()`.
        - `policy_management(configs)`: Determines installation policies (install, upgrade, downgrade, or skip).

    - **Utility Functions**:
        - `get_installed_filepath(configs)`: Retrieves the `installed.json` file path dynamically.
        - `print_installed_packages(configs)`: Displays a formatted list of installed packages.

Expected Behavior:
    - Dynamically adapts package installation based on system constraints.
    - Installs, upgrades, or downgrades packages per predefined policies.
    - Logs all package operations for debugging and troubleshooting.
    - Displays installed package statuses when requested.
    - Prevents unintended system modifications unless explicitly overridden.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to installation errors, missing configurations, or dependency issues.

Example:
    ```python
    from tracing import install_requirements
    install_requirements(configs=configs)
    ```
"""

import sys
import subprocess
import shutil

import json
import argparse
import platform

import importlib.metadata

from functools import lru_cache

from datetime import datetime, timezone
from typing import Optional, Union

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

from lib import system_variables as environment

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

# Global variable to store Brew availability
BREW_AVAILABLE = False

## -----------------------------------------------------------------------------

@lru_cache(maxsize=1)  # Cache the result to avoid redundant subprocess calls
def check_brew_availability() -> bool:
    """
    Check if Homebrew is available on macOS.

    Runs once at startup and stores the result in a global variable.

    Returns:
        bool: True if Brew is available on macOS, otherwise False.
    """

    if sys.platform != "darwin":
        return False  # Not macOS, so Brew isn't available

    # Fast check: If Brew binary is not found, return False immediately
    if not shutil.which("brew"):
        return False

    try:
        subprocess.run(
            [ "brew", "--version" ],
            capture_output=True,
            check=True,
            text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

## -----------------------------------------------------------------------------

def get_installed_filepath(configs: dict) -> Path:
    """
    Retrieve the installed.json file path from CONFIGS safely.

    Args:
        configs (dict): The configuration dictionary.

    Returns:
        Path: The path to installed.json.
    """
    return configs.get("packages", {}).get("installation", {}).get("configs", None)

## -----------------------------------------------------------------------------

def detect_python_environment(
    brew_available: bool
) -> dict:
    """
    Detects the Python installation method and whether it is externally managed.

    Args:
        brew_available (bool): Whether Homebrew is available (determined in main()).

    Returns:
        dict: A dictionary containing `INSTALL_METHOD`, `EXTERNALLY_MANAGED`, and `BREW_AVAILABLE`.
    """

    env_info = {
        "OS": platform.system().lower(),  # ✅ "windows", "linux", "darwin" (macOS)
        "INSTALL_METHOD": "standalone",   # Default to standalone Python installation
        "EXTERNALLY_MANAGED": False,      # Assume pip installs are allowed
        "BREW_AVAILABLE": brew_available  # Use precomputed Brew availability
    }

    # Check for EXTERNALLY-MANAGED marker (Linux/macOS)
    external_marker = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "EXTERNALLY-MANAGED"
    if external_marker.exists():
        env_info["EXTERNALLY_MANAGED"] = True

    # ✅ If Brew is available, determine if Python is installed via Brew
    if brew_available:
        try:
            result = subprocess.run(
                [ "brew", "--prefix", "python" ],
                capture_output=True,
                text=True,
                check=True
            )
            if result.returncode == 0:
                env_info["INSTALL_METHOD"] = "brew"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # ✅ Linux: Check if Python is installed via APT (Debian/Ubuntu) or DNF (Fedora)
    elif env_info["OS"] == "linux":
        try:
            result = subprocess.run(["dpkg", "-l", "python3"], capture_output=True, text=True)
            if "python3" in result.stdout:
                env_info["INSTALL_METHOD"] = "system"  # APT-managed
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    [ "rpm", "-q", "python3" ],
                    capture_output=True,
                    text=True
                )
                if "python3" in result.stdout:
                    env_info["INSTALL_METHOD"] = "system"  # DNF-managed
            except FileNotFoundError:
                pass

    # ✅ Windows: Check if Python is from Microsoft Store
    elif env_info["OS"] == "windows":
        try:
            result = subprocess.run(
                [ "python", "-m", "ensurepip" ],
                capture_output=True,
                text=True,
                check=True
            )
            if "externally-managed-environment" in result.stderr.lower():
                env_info["EXTERNALLY_MANAGED"] = True
                env_info["INSTALL_METHOD"] = "microsoft_store"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return env_info

## -----------------------------------------------------------------------------

@lru_cache(maxsize=None)  # Cache results for efficiency
def installed_version(package: str, configs: dict) -> Optional[str]:
    """
    Return the installed version of a package, checking Pip first, then OS-specific package managers.

    Args:
        package (str): The name of the package to check.
        configs (dict): The configuration dictionary containing environment details.

    Returns:
        Optional[str]: The installed version of the package as a string if found, otherwise None.
    """

    env = configs.get("environment", {})

    # ✅ 1. Check Pip (if allowed)
    if not env.get("EXTERNALLY_MANAGED", False):  # Only check Pip if not externally managed
        try:
            return importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass  # Continue to OS-specific package managers

    # ✅ 2. Use the correct package manager based on INSTALL_METHOD
    install_method = env.get("INSTALL_METHOD")

    match install_method:
        case "brew":
            return get_brew_version(package)
        case "system":
            return get_linux_version(package)
        case "microsoft_store":
            return get_windows_version(package)

    return None  # Package not found via any method

# ------------------------------------------------------

def get_brew_version(package: str) -> Optional[str]:
    """Retrieve the installed version of a package via Homebrew."""
    try:
        result = subprocess.run(
            [ "brew", "list", "--versions", package ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split()[-1] if result.stdout else None
    except subprocess.CalledProcessError:
        return None  # Brew package not found

# ------------------------------------------------------

def get_linux_version(package: str) -> Optional[str]:
    """Retrieve the installed version of a package via APT or DNF."""
    try:
        result = subprocess.run(
            [ "dpkg", "-s", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
    except FileNotFoundError:
        pass  # DPKG not found, try RPM

    try:
        result = subprocess.run(
            [ "rpm", "-q", package ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        return None  # RPM also not found

# ------------------------------------------------------

def get_windows_version(package: str) -> Optional[str]:
    """Retrieve the installed version of a package via Microsoft Store."""
    try:
        result = subprocess.run(
            [ "powershell", "-Command", f"(Get-AppxPackage -Name {package}).Version" ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.stdout else None
    except subprocess.CalledProcessError:
        return None  # Package not found in Microsoft Store

## -----------------------------------------------------------------------------

def get_brew_latest_version(package: str) -> Optional[str]:
    """Retrieve the latest available version of a package via Homebrew."""
    try:
        result = subprocess.run(
            [ "brew", "info", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "stable" in line:
                return line.split()[1]  # Extract version
    except subprocess.CalledProcessError:
        return None  # Brew failed

## -----------------------------------------------------------------------------

def get_pip_latest_version(package: str) -> Optional[str]:
    """Retrieve the latest available version of a package via Pip."""
    try:
        result = subprocess.run(
            [ sys.executable, "-m", "pip", "index", "versions", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "Available versions:" in line:
                versions = line.split(":")[1].strip().split(", ")
                return versions[0] if versions else None
    except subprocess.CalledProcessError:
        return None  # Pip failed

## -----------------------------------------------------------------------------

def get_linux_latest_version(package: str) -> Optional[str]:
    """Retrieve the latest available version of a package via APT or DNF."""
    try:
        result = subprocess.run(
            [ "apt-cache", "madison", package ],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            return result.stdout.splitlines()[0].split("|")[1].strip()  # Extract version
    except FileNotFoundError:
        pass  # Try DNF if APT is unavailable

    try:
        result = subprocess.run(
            [ "dnf", "list", "available", package ],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            return result.stdout.splitlines()[1].split()[1]  # Extract version
    except FileNotFoundError:
        return None  # No package manager found

## -----------------------------------------------------------------------------

def get_windows_latest_version(package: str) -> Optional[str]:
    """Retrieve the latest available version of a package via Microsoft Store."""
    try:
        result = subprocess.run(
            [ "powershell", "-Command", f"(Find-Package -Name {package}).Version" ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.stdout else None
    except subprocess.CalledProcessError:
        return None  # Package not found

## -----------------------------------------------------------------------------

@lru_cache(maxsize=None)  # Cache results for efficiency
def latest_version(package: str, configs: dict) -> Optional[str]:
    """
    Fetches the latest available version of a package using Pip or OS-specific package managers.

    Args:
        package (str): The package name to check.
        configs (dict): The configuration dictionary containing environment details.

    Returns:
        Optional[str]: The latest available version as a string if found, otherwise None.
    """

    env = configs.get("environment", {})

    # ✅ 1. Check Pip (if allowed)
    if not env.get("EXTERNALLY_MANAGED", False):  # Only check Pip if not externally managed
        latest_pip = get_pip_latest_version(package)
        if latest_pip:
            return latest_pip  # Return immediately if found

    # ✅ 2. Use the correct package manager based on INSTALL_METHOD
    install_method = env.get("INSTALL_METHOD")

    match install_method:
        case "brew":
            return get_brew_latest_version(package)
        case "system":
            return get_linux_latest_version(package)
        case "microsoft_store":
            return get_windows_latest_version(package)

    return None  # No version found

## -----------------------------------------------------------------------------

def install_packages(config_filepath: str, configs: dict) -> None:
    """
    Update the status of installed packages and write them to the installed JSON file.

    Args:
        config_filepath (str): The path to the installed.json file.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: Updates the installed package statuses and writes the data to installed.json.
    """

    env = configs.get("environment", {})
    dependencies = configs.get("requirements", None)  # ✅ No need to reload requirements
    installed_data = []

    for dep in dependencies:
        package = dep["package"]
        target_version = dep["version"]["target"]

        installed_version = installed_version(package, configs)

        # ✅ Determine package status
        if installed_version == target_version:
            status = "installed"
        elif installed_version and installed_version > target_version:
            status = "newer"
        elif installed_version and installed_version < target_version:
            status = "outdated"
        else:
            status = False  # Not installed

        installed_data.append({
            "package": package,
            "version": {
                "target": target_version,
                "installed": installed_version,
                "status": status
            }
        })

    # ✅ Write to installed.json **once** after processing all dependencies
    with open(config_filepath, "w") as file:
        json.dump({"dependencies": installed_data}, file, indent=4)

    log_utils.log_message(
        f'[INSTALL] Installed package status updated in {config_filepath}',
        configs=configs
    )

## -----------------------------------------------------------------------------

def install_requirements(configs: dict) -> None:
    """
    Installs, upgrades, or downgrades dependencies based on `policy_management()` results.

    This function processes the `requirements` list stored in `CONFIGS`, applies
    necessary package actions, and writes updated package statuses to `installed.json`.

    Args:
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: Performs installations/upgrades/downgrades based on policy decisions.
    """

    log_utils.log_message(
        f"[INSTALL] Starting installation process...",
        configs=configs
    )

    installed_filepath = get_installed_filepath(configs)  # ✅ Fetch dynamically
    if not installed_filepath.exists():
        log_utils.log_message(
            f"[ERROR] Missing installed.json path in CONFIGS.",
            configs=CONFIGS
        )
        sys.exit(1)  # Exit to prevent further failures

    # ✅ Use the `requirements` list from `CONFIGS`
    requirements = configs["requirements"]

    for dep in requirements:
        package = dep["package"]
        version_info = dep["version"]
        status = version_info["status"]
        target_version = version_info["target"]
        latest_version = version_info["latest"]
        policy_mode = version_info["policy"]

        if status == "installing":
            log_utils.log_message(
                f"[INSTALL] Installing {package} ({'latest' if policy_mode == 'latest' else target_version})...",
                configs=configs
            )
            # package_management(
            #     package,
            #     latest_version if policy_mode == "latest" else target_version,
            #     configs
            # )

        elif status == "upgrading":
            log_utils.log_message(
                f"[UPGRADE] Upgrading {package} to latest version ({latest_version})...",
                configs=configs
            )
            # package_management(package, None, configs)  # None means latest

        elif status == "downgraded":
            log_utils.log_message(
                f"[DOWNGRADE] Downgrading {package} to {target_version}...",
                configs=configs
            )
            # package_management(package, target_version, configs)

        elif status in ["restricted", "matched"]:
            log_utils.log_message(
                f"[SKIP] {package} is {status}, no changes needed.",
                configs=configs
            )

    # ✅ Write back to `installed.json` **only once** after processing all packages
    with installed_filepath.open("w") as f:
        json.dump({"dependencies": requirements}, f, indent=4)

    log_utils.log_message(
        f"[INSTALL] Installed.json updated at {installed_filepath}",
        configs=configs
    )
    log_utils.log_message(
        f"[INSTALL] Installation process completed.",
        configs=configs
    )

def print_installed_packages(configs: dict) -> None:
    """
    Print the installed dependencies in a readable format.

    This function reads the installed packages from the `installed.json` file and logs
    their names, required versions, installed versions, and current status.

    Args:
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: This function prints the installed package details but does not return any value.
    """

    installed_filepath = get_installed_filepath(configs)  # ✅ Fetch dynamically

    if not installed_filepath or not installed_filepath.exists():
        log_utils.log_message(
            f'[WARNING] Installed package file not found: {installed_filepath}',
            configs=configs
        )
        return

    try:
        with installed_filepath.open("r") as f:
            installed_data = json.load(f)

        dependencies = installed_data.get("dependencies", [])

        if not dependencies:
            log_utils.log_message(
                "[INFO] No installed packages found.",
                configs=configs
            )
            return

        log_utils.log_message("\n[INSTALLED PACKAGES]", configs=configs)

        for dep in dependencies:
            package = dep.get("package", "Unknown")
            target_version = dep.get("version", {}).get("target", "N/A")
            installed_version = dep.get("version", {}).get("installed", "Not Installed")
            status = dep.get("version", {}).get("status", "Unknown")

            log_utils.log_message(
                f'- {package} (Target: {target_version}, Installed: {installed_version}, Status: {status})',
                configs=configs
            )

    except json.JSONDecodeError:
        log_utils.log_message(
            f'[ERROR] Invalid JSON structure in {installed_filepath}.',
            configs=configs
        )

def package_management(
    package: str,
    version: Optional[str] = None,
    configs: dict = None
) -> None:
    """
    Install or update a package using Brew (if available) or Pip.

    - If Brew is available and managing Python, use Brew to install the package.
    - If Brew does NOT have the package, fall back to Pip:
      - If the environment is controlled and `--force` is NOT set, print instructions.
      - If `--force` is set, use Pip with `--break-system-packages`.
      - Otherwise, install via Pip with `--user` (default behavior).

    Args:
        package (str): The package name.
        version (Optional[str], default=None): The required version of the package.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: This function installs or updates the package, but does not return any value.
    """

    # ✅ Fetch environment details
    env_info = configs.get("environment", {})
    brew_available = env_info.get("INSTALL_METHOD") == "brew"  # ✅ Python is managed via Brew
    externally_managed = env_info.get("EXTERNALLY_MANAGED", False)  # ✅ Check if Pip is restricted
    forced_install = configs.get("packages", {}).get("installation", {}).get("forced", False)

    # ✅ 1️⃣ Check if Brew is available & controls Python
    if brew_available:
        log_utils.log_message(
            f'[INFO] Checking if "{package}" is available via Homebrew...',
            configs=configs
        )
        brew_list = subprocess.run(
            ["brew", "info", package],
            capture_output=True,
            text=True
        )

        if "Error:" not in brew_list.stderr:
            # ✅ If Brew has the package, install it
            log_utils.log_message(
                f'[INSTALL] Installing "{package}" via Homebrew...',
                configs=configs
            )
            subprocess.run(["brew", "install", package], check=False)
            return
        else:
            log_utils.log_message(
                f'[WARNING] Package "{package}" is not available via Brew. Falling back to Pip...',
                configs=configs
            )

    # ✅ 2️⃣ Use Pip (if Brew is not managing Python OR package not found in Brew)
    pip_install_cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--user"]

    if version:
        pip_install_cmd.append(f'{package}=={version}')
    else:
        pip_install_cmd.append(package)

    if externally_managed:
        # ✅ 2A: Pip is restricted → Handle controlled environment
        if forced_install:
            log_utils.log_message(
                f'[INSTALL] Installing "{package}" via Pip using `--break-system-packages` (forced mode)...',
                configs=configs
            )
            pip_install_cmd.append("--break-system-packages")
            subprocess.run(pip_install_cmd, check=False)
        else:
            log_utils.log_message(
                f'[INFO] "{package}" requires installation via Pip in a controlled environment.\n'
                f'Run the following command manually if needed:\n'
                f'    {sys.executable} -m pip install --user {package}',
                configs=configs
            )
    else:
        # ✅ 2B: Normal Pip installation (default)
        log_utils.log_message(
            f'[INSTALL] Installing "{package}" via Pip (default mode)...',
            configs=configs
        )
        subprocess.run(pip_install_cmd, check=False)

    return  # ✅ Exit after installation

## -----------------------------------------------------------------------------

def policy_management(configs: dict) -> list:
    """
    Evaluates package installation policies and updates the status of each dependency.

    Args:
        configs (dict): Configuration dictionary used for logging.

    Returns:
        list: The updated `requirements` list reflecting policy decisions.
    """

    dependencies = configs["requirements"]  # ✅ Use already-loaded requirements
    installed_filepath = get_installed_filepath(configs)  # ✅ Fetch dynamically

    for dep in dependencies:
        package = dep["package"]
        version_info = dep["version"]

        policy_mode = version_info.get("policy", "latest")  # Default to "latest"
        target_version = version_info.get("target")

        installed_ver = installed_version(package, configs)  # ✅ Get installed version
        available_ver = latest_version(package, configs)  # ✅ Get latest available version

        # ✅ Update version keys in `CONFIGS["requirements"]`
        version_info["latest"] = available_ver  # ✅ Store the latest available version
        version_info["status"] = False  # Default status before processing

        # ✅ Debugging
        print(f"\n[DEBUG] Evaluating package: {package}")
        print(f"        Target Version : {target_version}")
        print(f"        Installed Ver. : {installed_ver if installed_ver else 'Not Installed'}")
        print(f"        Latest Ver.    : {available_ver if available_ver else 'Unknown'}")
        print(f"        Policy Mode    : {policy_mode}")

        log_message = ""

        # Policy decision-making
        if not installed_ver:
            version_info["status"] = "installing"
            log_message = f"[POLICY] {package} is missing. Installing {'latest' if policy_mode == 'latest' else target_version}."

        elif installed_ver < target_version:
            if policy_mode == "latest":
                version_info["status"] = "upgrading"
                log_message = f"[POLICY] {package} is outdated ({installed_ver} < {target_version}). Upgrading..."
            else:
                version_info["status"] = "restricted"
                log_message = f"[POLICY] {package} is below target ({installed_ver} < {target_version}), but policy is restricted."

        elif installed_ver == target_version:
            if policy_mode == "latest" and available_ver > installed_ver:
                version_info["status"] = "outdated"
                log_message = f"[POLICY] {package} matches target but a newer version is available. Marking as outdated."
            else:
                version_info["status"] = "matched"
                log_message = f"[POLICY] {package} matches the target version. No action needed."

        else:  # installed_ver > target_version
            if policy_mode == "restricted":
                version_info["status"] = "downgraded"
                log_message = f"[POLICY] {package} is above target ({installed_ver} > {target_version}). Downgrading..."
            else:
                version_info["status"] = "upgraded"
                log_message = f"[POLICY] {package} is above target but latest policy applies. Keeping as upgraded."

        # ✅ Log once per package
        if log_message:
            log_utils.log_message(
                log_message,
                configs=configs
            )

    # ✅ Save modified `requirements` to `installed.json`
    try:
        with open(installed_filepath, "w") as f:
            json.dump({"dependencies": dependencies}, f, indent=4)
        log_message = f"[DEBUG] Installed.json updated at {installed_filepath}"
        print(log_message)
        log_utils.log_message(
            log_message,
            configs=configs
        )
    except Exception as e:
        error_message = f"[ERROR] Failed to write installed.json: {e}"
        print(error_message)
        log_utils.log_message(
            error_message,
            environment.category.error.id,
            configs=configs
        )

    return dependencies  # ✅ Explicitly return the modified requirements list

## -----------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for specifying the requirements file
    and displaying the installed dependencies.

    Args:
        None

    Returns:
        argparse.Namespace: The parsed arguments object containing selected options.

    Return Type: argparse.Namespace
        Returns an argparse.Namespace object containing the parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Manage package dependencies using Brew and PIP using policy management. "
                    "Use -c/--config to specify a custom JSON configuration file."
                    "Use --show-installed to display installed dependencies."
                    "Use -f/--force to request PIP to install using --break-system-packages."
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
        "--show-installed",
        action="store_true",
        help="Display the contents of installed.json"
    )
    return parser.parse_args()

## -----------------------------------------------------------------------------

def main() -> None:
    """
    Entry point for the package installer. Sets up logging, processes command-line arguments,
    and installs or updates dependencies from a JSON requirements file.

    This function:
        - Detects the Python environment (Brew, system-managed, standalone).
        - Determines if Pip installations require `--force`.
        - Loads the configuration file and processes package installations.

    Args:
        None

    Returns:
        None: This function serves as the main entry point, performing actions based on
              the command-line arguments, such as installing or updating dependencies.
    """

    # Ensure the variable exists globally
    global CONFIGS, BREW_AVAILABLE

    args = parse_arguments()

    CONFIGS = tracing.setup_logging(events=False)
    # CONFIGS = tracing.setup_logging(events=["call", "return"])

    # Load the JSON file contents before passing to policy_management
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
        "Initializing Package Dependencies Management process...",
        configs=CONFIGS
    )

    # ✅ Get the directory of `requirements.json`
    installed_filepath = location.parent / "installed.json"  # ✅ Ensures the correct file path

    # ✅ Ensure the file exists; if not, create an empty JSON object
    if not installed_filepath.exists():
        log_utils.log_message(
            f"[INFO] Creating missing installed.json at {installed_filepath}",
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

    if args.show_installed:

        if installed_filepath.exists():
            with installed_filepath.open("r") as f:
                print(json.dumps(json.load(f), indent=4))
        else:
            print(f"[INFO] No {installed_filepath} found.")
        return  # Exit after showing installed packages

    BREW_AVAILABLE = check_brew_availability()  # Run once at startup
    print(f"[DEBUG] Brew Available?: {BREW_AVAILABLE}")

    environment_info = detect_python_environment(brew_available=BREW_AVAILABLE)
    log_utils.log_message(
        f"[ENVIRONMENT] Detected Python Environment: {json.dumps(environment_info, indent=4)}",
        configs=CONFIGS
    )
    CONFIGS.setdefault("environment", {}).update(environment_info)

    CONFIGS["requirements"] = policy_management(
        configs=CONFIGS
    )

    install_requirements( configs=CONFIGS )

    print(
        f'CONFIGS: {json.dumps(
            CONFIGS,
            indent=environment.default_indent
        )}')

    # install_packages(
    #     requirements=args.requirements,
    #     config_filepath=config_filepath,
    #     configs=CONFIGS
    # )

    log_utils.log_message(
        f'Logs are being saved in: {CONFIGS["logging"].get("log_filename")}',
        configs=CONFIGS
    )

if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     choice = input("Would you like to (1) Backup or (2) Restore packages? ")
#     if choice == "1":
#         backup_installed_packages()
#     elif choice == "2":
#         restore_installed_packages()
#     else:
#         print("Invalid choice. Exiting.")
