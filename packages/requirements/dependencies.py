#!/usr/bin/env python3

"""
File Path: packages/installer/install_requirements.py

Description:
    Dependency Management System
    This module handles the installation and verification of dependencies listed
    in a JSON requirements file. It supports both Pip and Brew (for macOS) package
    managers to ensure the correct versions of dependencies are installed and up-to-date.

Core Features:
    - **Install Missing Dependencies**: Installs missing or outdated packages from a JSON file.
    - **Verify Installed Packages**: Checks installed versions of packages and ensures compliance with the requirements.
    - **Update Installed Packages**: Updates packages if necessary, ensuring all dependencies are correctly installed.
    - **Show Installed Packages**: Displays the installed versions of dependencies, highlighting any discrepancies.

Usage:
    To install or update dependencies:
    ```python
    from install_requirements import install_requirements
    install_requirements(requirements_file="requirements.json", configs=configs)
    ```

    To show the installed packages:
    ```bash
    python install_requirements.py --show-installed
    ```

Dependencies:
    - subprocess
    - argparse
    - json
    - importlib.metadata
    - pathlib
    - datetime
    - lib.system_variables (for project-wide configurations)
    - lib.pkgconfig_loader (for configuration handling)
    - lib.log_utils (for logging messages)
    - packages.appflow_tracer (for tracing setup)

Global Variables:
    - `CONFIGS`: Stores the effective configurations used for logging and package installation.
    - `LIB_DIR`: Directory path for the `lib` directory.
    - `requirements_file`: Path to the JSON file containing the dependencies.

Primary Functions:
    - `load_requirements(requirements_file, configs)`: Loads and parses the requirements JSON file.
    - `get_installed_version(package)`: Returns the installed version of a package, checking both Pip and Brew.
    - `install_requirements(requirements_file, configs)`: Installs or updates the required dependencies listed in the JSON file.
    - `install_or_update_package(package, version, configs)`: Installs or updates a specific package using Pip or Brew.
    - `is_brew_available()`: Checks if Brew (for macOS) is available on the system.
    - `is_package_installed(package, version_info, configs)`: Verifies whether a package is installed and meets the required version.
    - `parse_arguments()`: Parses the command-line arguments for specifying the requirements file and showing installed dependencies.
    - `print_installed_packages(config_filepath, configs)`: Prints the installed packages in a human-readable format.
    - `update_installed_packages(requirements_file, config_filepath, configs)`: Updates the status of installed packages and writes them to the installed JSON file.

Expected Behavior:
    - Installs or updates packages listed in the JSON file to ensure they are up-to-date.
    - Verifies installed versions and logs appropriate messages.
    - Displays installed packages and their statuses when requested.
    - Logs the installation and verification process to assist with debugging.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to errors in installation, package not found, or missing configurations.

Example:
    ```python
    from install_requirements import install_requirements
    install_requirements("requirements.json", configs)
    ```
"""

import sys
import subprocess
import argparse
import json

import importlib.metadata

from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Union

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils
from lib import system_variables as environment

def load_requirements(
    requirements_file: str,
    configs: dict
) -> list:
    """
    Load the dependencies from a JSON requirements file.

    This function parses the JSON file, ensuring it contains the required dependencies
    and extracting the package names and their versions.

    Args:
        requirements_file (str): The path to the requirements JSON file.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        list: A list of dictionaries containing package names and their respective versions.
              Each dictionary contains the keys:
                - 'package' (str): The package name.
                - 'version' (dict): A dictionary with the package version.

    Raises:
        FileNotFoundError: If the requirements file does not exist.
        ValueError: If the JSON structure is invalid or the 'dependencies' key is missing.
    """

    requirements_path = Path(requirements_file).resolve()
    if not requirements_path.exists():
        log_utils.log_message(
            f'Requirements file not found: {requirements_path}',
            environment.category.error.id,
            configs=configs
        )
        raise FileNotFoundError(
            f'ERROR: Requirements file not found at {requirements_path}'
        )
    try:
        with open(requirements_path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "dependencies" not in data:
                raise ValueError(
                    "Invalid JSON format: Missing `dependencies` key."
                )

            dependencies = [
                {
                    "package": pkg["package"],
                    "version": pkg["version"]
                } for pkg in data.get("dependencies", [])
            ]
            return dependencies
    except json.JSONDecodeError as e:
        log_utils.log_message(
            f'Invalid JSON in "{requirements_path}": {e}',
            environment.category.error.id,
            configs=configs
        )
        raise ValueError(
            f'ERROR: Invalid JSON structure in "{requirements_path}".\nDetails: {e}'
        )

def get_installed_version(
    package: str
) -> Optional[str]:
    """
    Return the installed version of a package, first checking Pip, then Brew.

    This function first checks if the package is installed via Pip, and if not,
    checks if it is available via Brew (macOS).

    Args:
        package (str): The name of the package to check.

    Returns:
        Optional[str]: The installed version of the package as a string if found, otherwise None.
    """

    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        pass  # Continue to check Brew
    if is_brew_available():
        try:
            result = subprocess.run(
                ["brew", "list", "--versions", package],
                capture_output=True,
                text=True,
                check=True
            )
            brew_installed_version = result.stdout.strip().split()[-1] if result.stdout else None
            if brew_installed_version:
                return brew_installed_version
        except subprocess.CalledProcessError:
            pass  # If Brew check fails, return None
    return None  # If neither Pip nor Brew has the package

# def install_requirements(
#     requirements_file: str,
#     configs: dict
# ) -> None:
#
#     dependencies = load_requirements(
#         requirements_file=requirements_file,
#         configs=configs
#     )
#     if not dependencies:
#         log_utils.log_message(
#             "No dependencies found in requirements.json",
#             environment.category.warning.id,
#             configs=configs
#         )
#         return
#     for dep in dependencies:
#         package = dep["package"]
#         version = dep["version"]
#         install_or_update_package(
#             package=package,
#             version=version["target"],
#             configs=configs
#         )

def install_requirements(
    requirements_file: str,
    configs: dict
) -> None:
    """
    Install missing dependencies from a JSON requirements file.

    This function iterates through the dependencies listed in the requirements file,
    checking if they are installed and installing missing or outdated packages.

    Args:
        requirements_file (str): The path to the JSON requirements file.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: This function performs installations or updates but does not return any value.
    """

    dependencies = load_requirements(
        requirements_file=requirements_file,
        configs=configs
    )
    if not dependencies:
        log_utils.log_message(
            "No dependencies found in requirements.json",
            environment.category.warning.id,
            configs=configs
        )
        return
    for dep in dependencies:
        package = dep["package"]
        version = dep["version"]["target"]
        installed_version = get_installed_version(package)
        if installed_version == version:
            log_utils.log_message(
                f'{package} {installed_version} is already installed. Skipping installation.',
                configs=configs
            )
            continue  # Fix: Skip calling `install_or_update_package` if version matches**
        log_utils.log_message(
            f'{package} is missing or outdated. Installing...',
            configs=configs
        )
        install_or_update_package(
            package=package,
            version=version,
            configs=configs
        )

def install_or_update_package(
    package: str,
    version: str = None,
    configs: dict = None
) -> None:
    """
    Install or update a package using Brew (if available) or Pip.

    This function attempts to install or update a package by first checking if Brew
    is available and then trying to install or upgrade using Pip if necessary.

    Args:
        package (str): The package name.
        version (str, optional): The required version of the package (default: None).
        configs (dict, optional): Configuration dictionary used for logging (default: None).

    Returns:
        None: This function installs or updates the package, but does not return any value.
    """

    installed_version = get_installed_version(package)
    if installed_version == version:
        log_utils.log_message(
            f'{package} {installed_version} is already installed.',
            configs=configs
        )
        return
    if is_brew_available():
        log_utils.log_message(
            f'Checking {package} installation via Brew...',
            configs=configs
        )
        try:
            brew_info = subprocess.run(
                ["brew", "list", "--versions", package],
                capture_output=True, text=True, check=True
            )
            brew_installed_version = brew_info.stdout.strip().split()[-1] if brew_info.stdout else None
        except subprocess.CalledProcessError:
            brew_installed_version = None
        # If package exists in Brew and needs upgrade
        if brew_installed_version:
            if version and brew_installed_version != version:
                log_utils.log_message(
                    f'Upgrading {package} to {version} via Brew...',
                    configs=configs
                )
                subprocess.run(
                    ["brew", "upgrade", package],
                    check=True
                )
            else:
                log_utils.log_message(
                    f'{package} {brew_installed_version} is already up to date (Brew).',
                    configs=configs
                )
            return
        # If Brew is available but doesn't have the package, try installing via Brew
        log_utils.log_message(
            f'Installing {package} via Brew...',
            configs=configs
        )
        subprocess.run(
            ["brew", "install", package],
            check=True
        )
        return
    # If Brew isn't an option, install via Pip
    log_utils.log_message(
        f'Installing {package} via Pip...',
        configs=configs
    )
    pip_install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet"
    ]
    if version:
        pip_install_cmd.append(f'{package}=={version}')
    else:
        pip_install_cmd.append(package)
    try:
        subprocess.run(
            pip_install_cmd,
            check=True
        )
        log_utils.log_message(
            f'Successfully installed {package} via Pip.',
            configs=configs
        )
    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'Failed to install {package} via Pip. Error: {e}',
            environment.category.error.id,
            configs=configs
        )

def is_brew_available() -> bool:
    """
    Check if Homebrew is available on macOS.

    This function checks whether the system is running on macOS and if Homebrew is installed.

    Returns:
        bool: True if Brew is available on macOS, otherwise False.
    """

    if sys.platform != "darwin":
        return False
    try:
        subprocess.run(
            ["brew", "--version"],
            capture_output=True,
            check=True,
            text=True
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError
    ):
        return False

def is_package_installed(
    package: str,
    version_info: dict,
    configs: dict
) -> bool:
    """
    Check if a package is installed and meets the required version.

    This function checks if a package is installed, either via Pip or Brew (on macOS),
    and verifies that the installed version meets the specified version requirement.

    Args:
        package (str): The package name.
        version_info (dict): Dictionary containing version information.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        bool: True if the package is installed and the version matches the requirement,
              otherwise False.
    """

    version = version_info.get("target")
    if not version:
        log_utils.log_message(
            f'Skipping {package}: Missing "target" version.',
            environment.category.warning.id,
            configs=configs
        )
        return False
    brew_version = None
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["brew", "list", "--versions", package],
                capture_output=True,
                text=True,
                check=True
            )
            brew_version = result.stdout.strip().split()[-1] if result.stdout else None
            if brew_version == version:
                log_utils.log_message(
                    f'{package}=={brew_version} detected via Brew.',
                    configs=configs
                )
                return True
            elif brew_version:
                log_utils.log_message(
                    f'{package} installed via Brew, but version {brew_version} != {version} (expected).',
                    environment.category.warning.id,
                    configs=configs
                )
        except subprocess.CalledProcessError:
            pass  # Brew check failed, continue with Pip check
    try:
        installed_version = importlib.metadata.version(package)
        if installed_version == version:
            log_utils.log_message(
                f'{package}=={installed_version} is installed (Pip detected).',
                configs=configs
            )
            return True
        else:
            log_utils.log_message(
                f'{package} installed, but version {installed_version} != {version} (expected).',
                environment.category.warning.id,
                configs=configs
            )
            return False
    except importlib.metadata.PackageNotFoundError:
        if not brew_version:
            log_utils.log_message(
                f'{package} is NOT installed via Pip or Brew.',
                environment.category.error.id,
                configs=configs
            )
        return False

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
        description="Verify installed dependencies for compliance. "
                    "Use -f to specify a custom JSON file. Use --show-installed to display installed dependencies."
    )
    parser.add_argument(
        "-f", "--file",
        dest="requirements_file",
        default="./packages/requirements/requirements.json",
        help="Path to the requirements JSON file (default: ./packages/requirements/requirements.json)"
    )
    parser.add_argument(
        "--show-installed",
        action="store_true",
        help="Display the contents of installed.json"
    )
    return parser.parse_args()

def print_installed_packages(
    config_filepath: str,
    configs: dict
) -> None:
    """
    Print the installed dependencies in a readable format.

    This function reads the installed packages from the specified file and logs
    their names, required versions, installed versions, and current status.

    Args:
        config_filepath (str): Path to the installed.json file.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: This function prints the installed package details but does not return any value.
    """

    if not Path(config_filepath).exists():
        log_utils.log_message(
            f'Installed package file not found: {config_filepath}',
            configs=configs
        )
        return
    try:
        with open(config_filepath, "r") as f:
            installed_data = json.load(f)
        log_utils.log_message(
            "\nInstalled Packages:\n",
            configs=configs
        )
        for dep in installed_data.get("dependencies", []):
            package = dep["package"]
            target_version = dep["version"]["target"]
            installed_version = dep["version"].get("installed", "Not Installed")
            status = dep["version"]["status"]

            # status_icon = "Ok" if status == "installed" else "Missing"
            log_utils.log_message(
                f'{package} (Required: {target_version}, Installed: {installed_version})',
                configs=configs
            )
    except json.JSONDecodeError:
        log_utils.log_message(
            f'Error: Invalid JSON structure in {config_filepath}',
            configs=configs
        )

def update_installed_packages(
    requirements_file: str,
    config_filepath: str,
    configs: dict
) -> None:
    """
    Update the status of installed packages and write them to the installed JSON file.

    This function checks the installed versions of the packages listed in the requirements
    file and updates the status (installed, outdated, or newer) before writing the information
    to the installed.json file.

    Args:
        requirements_file (str): The path to the requirements JSON file.
        config_filepath (str): The path to the installed.json file.
        configs (dict): Configuration dictionary used for logging.

    Returns:
        None: This function updates the installed package statuses and writes the data
              to the installed.json file, without returning any value.
    """

    dependencies = load_requirements(
        requirements_file,
        configs=configs
    )
    installed_data = []
    for dep in dependencies:
        package = dep["package"]
        target_version = dep["version"]["target"]
        # First, try to get version via Pip
        try:
            installed_version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed_version = None  # Pip does not have it
        # If Pip fails, check Brew
        if installed_version is None and is_brew_available():
            try:
                result = subprocess.run(
                    ["brew", "list", "--versions", package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                installed_version = result.stdout.strip().split()[-1] if result.stdout else None
            except subprocess.CalledProcessError:
                installed_version = None  # Brew also failed
        # Determine package status
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
    # Write to installed.json
    log_utils.log_message(
        f'Installed JSON file: {config_filepath}',
        configs=configs
    )
    with open(config_filepath, "w") as file:
        json.dump(
            {"dependencies": installed_data},
            file,
            indent=4
        )
    log_utils.log_message(
        f'Installed package status updated in {config_filepath}',
        configs=configs
    )

# ---------- Module Global variables:

# ---------- Module operations:

def main() -> None:
    """
    Entry point for the package installer. Sets up logging, processes command-line arguments,
    and installs or updates dependencies from a JSON requirements file.

    Args:
        None

    Returns:
        None: This function serves as the main entry point, performing actions based on
              the command-line arguments, such as installing or updating dependencies.
    """

    # Ensure the variable exists globally
    global CONFIGS
    # CONFIGS = tracing.setup_logging(events=False)
    CONFIGS = tracing.setup_logging(events=["call", "return"])
    print( f'CONFIGS: {json.dumps(CONFIGS, indent=environment.default_indent)}' )
    packages = environment.project_root / "packages" / CONFIGS["logging"].get("package_name")
    config_filepath = packages / "installed.json"
    args = parse_arguments()
    if args.show_installed:
        print_installed_packages(
            config_filepath=config_filepath,
            configs=CONFIGS
        )
        return  # Exit after displaying installed.json

    log_utils.log_message(
        "Starting dependency installation process...",
        configs=CONFIGS
    )
    install_requirements(
        requirements_file=args.requirements_file,
        configs=CONFIGS
    )
    update_installed_packages(
        requirements_file=args.requirements_file,
        config_filepath=config_filepath,
        configs=CONFIGS
    )
    log_utils.log_message(
        f'Logs are being saved in: {CONFIGS["logging"].get("log_filename")}',
        configs=CONFIGS
    )

if __name__ == "__main__":
    main()
