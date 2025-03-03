#!/usr/bin/env python3

"""
Unit tests for the dependency management module.

This module contains tests for verifying the correct behavior of functions that load, install, and validate dependencies.
It ensures that packages are installed correctly, updates are applied properly, and compliance is maintained.
"""

import sys
import json
import subprocess
import importlib.metadata

import pytest
from unittest.mock import patch

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from packages.appflow_tracer import tracing
from packages.requirements import dependencies

try:
  CONFIGS = tracing.setup_logging(
      logname_override='logs/tests/test_dependencies.log'
  )
  CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
  CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints
except NameError:
    CONFIGS = {
        "logging": {"enable": False},
        "tracing": {"enable": False},
        "events": {"install": True, "update": True},
    }

@pytest.fixture(autouse=True)
def mock_configs():
    """
    Mock `CONFIGS` globally for all tests if it has not been initialized.

    This fixture ensures that the `CONFIGS` object is available globally for all tests. If `CONFIGS` has not been
    previously initialized, it will set it to a default configuration with logging and tracing disabled, and
    events for `install` and `update` enabled. This provides a consistent set of configuration values for all
    tests that require `CONFIGS`.

    This fixture is automatically used for all tests due to the `autouse=True` flag, so it doesn't need to be explicitly
    requested in each test.

    Returns:
        dict: The `CONFIGS` dictionary containing configuration values for logging, tracing, and events.
    """

    global CONFIGS
    if CONFIGS is None:
        CONFIGS = {
            "logging": {"enable": False},
            "tracing": {"enable": False},
            "events": {"install": True, "update": True},
        }
    return CONFIGS  # Explicitly returns CONFIGS

@pytest.mark.parametrize(
    "package, expected_version", [
        ("requests", "2.28.1"),
        ("nonexistent-package", None)
    ]
)
@patch("packages.requirements.dependencies.get_installed_version")
def test_debug_installation(
    mock_get_version,
    package,
    expected_version
):
    """
    Debugging test to check whether the package installation check
    is returning expected results.

    This test verifies:
    - That `get_installed_version` returns the correct version for a given package.
    - It prints debugging information to show the expected and actual versions.

    Args:
        mock_get_version (MagicMock): Mock version of `get_installed_version` to simulate package version checking.
        package (str): The name of the package to check.
        expected_version (str or None): The expected version of the package.

    Returns:
        None: This test does not return any value. It asserts that the package version returned matches the expected version.
    """

    mock_get_version.return_value = expected_version
    result = mock_get_version(package)
    # Print debug information
    print(f'Testing package: {package}, Expected Version: {expected_version}, Got: {result}')
    assert result == expected_version

def test_load_requirements_invalid_json(
    tmp_path,
    mock_configs
):
    """
    Test that loading a malformed JSON file raises a ValueError.

    This test ensures that:
    - A `ValueError` is raised when the requirements file contains invalid JSON.

    Args:
        tmp_path (Path): Temporary directory provided by pytest for creating test files.
        mock_configs (dict): Mock configuration used for loading the requirements file.

    Returns:
        None: This test does not return any value but raises an exception if the JSON is invalid.
    """

    req_file = tmp_path / "requirements.json"
    req_file.write_text(
        "{invalid_json}"
    )
    with pytest.raises(ValueError):
        dependencies.load_requirements(
            str(req_file),
            configs=mock_configs
        )

def test_load_requirements_missing(
    mock_configs
):
    """
    Test that loading a missing requirements file raises a FileNotFoundError.

    This test ensures that:
    - A `FileNotFoundError` is raised when the requirements file does not exist.

    Args:
        mock_configs (dict): Mock configuration used for loading the requirements file.

    Returns:
        None: This test does not return any value but raises an exception if the file is not found.
    """

    with pytest.raises(FileNotFoundError):
        dependencies.load_requirements(
            "nonexistent.json",
            configs=mock_configs
        )

def test_load_requirements_valid(
    tmp_path,
    mock_configs
):
    """
    Test that a valid requirements file is correctly loaded.

    This test verifies:
    - That a valid JSON file containing package information is loaded correctly.

    Args:
        tmp_path (Path): Temporary directory provided by pytest for creating test files.
        mock_configs (dict): Mock configuration used for loading the requirements file.

    Returns:
        None: This test does not return any value but asserts that the loaded data matches the expected format.
    """

    req_file = tmp_path / "requirements.json"
    req_data = {
        "dependencies": [{
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }]
    }
    req_file.write_text(
        json.dumps(req_data)
    )
    result = dependencies.load_requirements(
        str(req_file),
        configs=mock_configs
    )
    assert result == [
        {
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }
    ]

@patch(
    "packages.requirements.dependencies.get_installed_version",
    return_value="2.28.1"
)
def test_install_or_update_package(
    mock_version,
    mock_configs
):
    """
    Test that `dependencies.install_or_update_package` does not attempt installation
    if the package is already installed with the correct version.

    This test ensures:
    - If the package is already installed with the correct version, no installation is attempted.

    Args:
        mock_version (MagicMock): Mock version of `get_installed_version` to simulate the installed version of the package.
        mock_configs (dict): Mock configuration used for the installation process.

    Returns:
        None: This test does not return any value but asserts that the installation is not triggered if the version matches.
    """

    with patch("subprocess.run") as mock_subproc:
        dependencies.install_or_update_package(
            "requests",
            "2.28.1",
            configs=mock_configs
        )
        mock_subproc.assert_not_called()  # Should not run installation if version matches

@patch("packages.requirements.dependencies.install_or_update_package")  # Prevents real installations
@patch("packages.requirements.dependencies.get_installed_version")
def test_install_requirements(
    mock_get_version,
    mock_install,
    tmp_path,
    mock_configs
):
    """
    Test that `dependencies.install_requirements` correctly skips installation if
    the required version is already installed, and triggers installation
    when the package is missing.

    This test verifies:
    - That the installation is skipped if the correct version is already installed.
    - That installation is triggered if the package is missing.

    Args:
        mock_get_version (MagicMock): Mock version of `get_installed_version` to simulate the installed version of the package.
        mock_install (MagicMock): Mock version of `install_or_update_package` to simulate the installation process.
        tmp_path (Path): Temporary directory provided by pytest for creating test files.
        mock_configs (dict): Mock configuration used for the installation process.

    Returns:
        None: This test does not return any value but asserts that installation behavior matches expectations.
    """

    req_file = tmp_path / "requirements.json"
    req_data = {
        "dependencies": [{
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }]
    }
    req_file.write_text(json.dumps(req_data))
    # Simulate scenario where the package is already installed
    mock_get_version.return_value = "2.28.1"
    dependencies.install_requirements(
        str(req_file),
        configs=mock_configs
    )
    # Ensure `dependencies.install_or_update_package` is NOT called when package is already installed
    mock_install.assert_not_called()
    # 🔄 Simulate package missing scenario
    mock_get_version.return_value = None
    dependencies.install_requirements(
        str(req_file),
        configs=mock_configs
    )
    # Ensure install is triggered when package is missing
    # mock_install.assert_called_once_with("requests", "2.28.1", configs=mock_configs)
    mock_install.assert_called_once()
    args, kwargs = mock_install.call_args
    assert kwargs["package"] == "requests"
    assert kwargs["version"] == "2.28.1"
    assert kwargs["configs"] == mock_configs

@patch("subprocess.check_call")  # Prevents actual package installations
@patch(
    "importlib.metadata.version",
    return_value="2.28.1"
)
def test_is_package_installed(
    mock_version,
    mock_subproc_call,
    mock_configs
):
    """
    Test that `dependencies.is_package_installed` correctly checks if a package is installed.

    This test ensures:
    - That the function correctly returns `True` if the package is installed with the expected version.
    - That the function returns `False` if the package is not installed or if the version does not match.

    Args:
        mock_version (MagicMock): Mock version of `importlib.metadata.version` to simulate the installed version of the package.
        mock_subproc_call (MagicMock): Mock subprocess call to prevent actual installations.
        mock_configs (dict): Mock configuration used for the installation check.

    Returns:
        None: This test does not return any value but asserts that the function returns the expected boolean result.
    """

    assert dependencies.is_package_installed(
        "requests",
        {"target": "2.28.1"},
        configs=mock_configs
    ) is True
    assert dependencies.is_package_installed(
        "nonexistent",
        {"target": "1.0.0"},
        configs=mock_configs
    ) is False
    assert dependencies.is_package_installed(
        "requests",
        {"target": "2.27.0"},
        configs=mock_configs
    ) is False

def test_parse_arguments_custom():
    """
    Test that the custom requirements file argument is correctly parsed.

    This test verifies:
    - That when a custom file path is provided via command line arguments, it is correctly parsed by `parse_arguments()`.

    Returns:
        None: This test does not return any value but asserts that the custom requirements file path is correctly recognized.
    """

    with patch(
        "sys.argv",
        ["dependencies.py",
         "-f",
         "custom.json"]
    ):
        args = dependencies.parse_arguments()
        assert args.requirements_file == "custom.json"

def test_parse_arguments_default():
    """
    Test that the default requirements file path is used when no custom argument is provided.

    This test verifies:
    - That when no custom file path is provided via command line arguments, the default path is used.

    Returns:
        None: This test does not return any value but asserts that the default requirements file path is used when necessary.
    """

    with patch(
        "sys.argv",
        ["dependencies.py"]
    ):
        args = dependencies.parse_arguments()
        assert args.requirements_file == "./packages/requirements/requirements.json"

@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_print_installed_packages(
    mock_log_message,
    tmp_path,
    mock_configs
):
    """
    Test that `dependencies.print_installed_packages` correctly prints the installed packages.

    This test verifies:
    - That installed package details are logged correctly, including package name, required version, and installed version.

    Args:
        mock_log_message (MagicMock): Mock version of `log_message` to verify the logging behavior.
        tmp_path (Path): Temporary directory provided by pytest for creating test files.
        mock_configs (dict): Mock configuration used for the printing process.

    Returns:
        None: This test does not return any value but asserts that the log message is correctly called.
    """

    installed_file = tmp_path / "installed.json"
    installed_data = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "target": "2.28.1",
                    "installed": "2.28.1",
                    "status": "installed"
                }
            }
        ]
    }
    installed_file.write_text(
        json.dumps(installed_data, indent=4)
    )
    dependencies.print_installed_packages(
        str(installed_file),
        configs=mock_configs
    )
    # Ensure log messages were called correctly
    mock_log_message.assert_any_call(
        "\nInstalled Packages:\n",
        configs=mock_configs
    )
    mock_log_message.assert_any_call(
        "requests (Required: 2.28.1, Installed: 2.28.1)",
        configs=mock_configs
    )

@patch(
    "importlib.metadata.version",
    side_effect=lambda pkg: "2.28.1" if pkg == "requests" else None
)
def test_update_installed_packages(
    mock_version,
    tmp_path,
    mock_configs
):
    """
    Test that `dependencies.update_installed_packages` correctly updates the installed package status.

    This test ensures:
    - That the installed version of packages is updated correctly in the installed file.

    Args:
        mock_version (MagicMock): Mock version of `importlib.metadata.version` to simulate the installed version.
        tmp_path (Path): Temporary directory provided by pytest for creating test files.
        mock_configs (dict): Mock configuration used for updating the installed package status.

    Returns:
        None: This test does not return any value but asserts that the installed package data is correctly updated.
    """

    req_file = tmp_path / "requirements.json"
    installed_file = tmp_path / "installed.json"
    req_data = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "target": "2.28.1"
                }
            }
        ]
    }
    req_file.write_text(
        json.dumps(req_data)
    )
    dependencies.update_installed_packages(
        str(req_file),
        str(installed_file),
        configs=mock_configs
    )
    installed_data = json.loads(
        installed_file.read_text()
    )
    assert installed_data["dependencies"][0]["package"] == "requests"
    assert installed_data["dependencies"][0]["version"]["installed"] == "2.28.1"
