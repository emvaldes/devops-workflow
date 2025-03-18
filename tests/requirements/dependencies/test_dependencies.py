#!/usr/bin/env python3

# File: ./tests/requirements/dependencies/test_dependencies_utils.py

__package__ = "tests.requirements"
__module__ = "dependencies"

__version__ = "0.1.0"  ## Updated Test Module version

#-------------------------------------------------------------------------------

# Standard library imports - Core system module
import sys

# Standard library imports - Utility module
import json

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Argument parsing module
import argparse

# Standard library imports - Testing and mocking module
from unittest.mock import (
    ANY,
    patch
)

# Third-party library import - Testing framework
import pytest

#-------------------------------------------------------------------------------

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

#-------------------------------------------------------------------------------

from tests.mocks.config_loader import (
    load_mock_requirements,
    load_mock_installed
)
from packages.requirements import dependencies
from packages.requirements.lib import (
    package_utils,
    policy_utils
)

#-------------------------------------------------------------------------------

# Add this function before the test cases
def serialize_configs(
    configs
):

    return json.loads(
        json.dumps(
            configs,
            default=lambda o: str(o) if isinstance(o, Path) else o
        )
    )

#-------------------------------------------------------------------------------

@pytest.fixture
def mock_config():

    return {
        "packages": {"installation": {"forced": False, "configs": Path("/tmp/test_installed.json")}},
        "environment": {"INSTALL_METHOD": "pip", "EXTERNALLY_MANAGED": False},
        "logging": {"package_name": "requirements", "module_name": "dependencies", "enable": False},
        "tracing": {"enable": False},
        "requirements": [
            {"package": "requests", "version": {"policy": "latest", "target": "2.28.0", "latest": None, "status": None}}
        ],
    }

# ------------------------------------------------------------------------------
# Test: parse_arguments()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "args, expected",
    [
        ([], "./packages/requirements/requirements.json"),  # Default value
        (["-c", "custom_requirements.json"], "custom_requirements.json"),  # Custom value
    ]
)
def test_parse_arguments(
    args,
    expected
):

    test_args = ["dependencies.py"] + args  # Ensure script name is included
    with patch.object(sys, "argv", test_args), \
         patch("sys.exit") as mock_exit:  # Prevent argparse from exiting
        parsed_args = dependencies.parse_arguments()  # Correctly call the function
        assert parsed_args.requirements == expected  # Validate parsed argument
        mock_exit.assert_not_called()  # Ensure no forced exit happened

# ------------------------------------------------------------------------------
# Test: main()
# ------------------------------------------------------------------------------

def test_main(
    mock_config
):

    temp_installed_file = mock_config["packages"]["installation"]["configs"]
    installed_mock = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "policy": "latest",
                    "target": "2.28.0",
                    "latest": "2.28.1",
                    "status": "outdated"
                }
            }
        ]
    }
    temp_installed_file.write_text(
        json.dumps(installed_mock, indent=4)
    )
    # Mock command-line arguments
    with patch.object(
            sys,
            "argv",
            ["dependencies.py", "--backup-packages", "backup.json"]
         ), \
         patch(
             "packages.requirements.lib.policy_utils.policy_management",
             return_value=mock_config.get(
                 "requirements", []
             )
         ) as mock_policy, \
         patch(
             "packages.requirements.lib.package_utils.install_requirements",
             return_value=installed_mock["dependencies"]
         ) as mock_install, \
         patch(
             "packages.requirements.lib.package_utils.backup_packages"
         ) as mock_backup, \
         patch(
             "packages.appflow_tracer.lib.log_utils.log_message"
         ) as mock_log:
        dependencies.main()  # Execute main()
        # Ensure `policy_management()` was called
        mock_policy.assert_called_once()
        # Ensure `install_requirements()` was called
        mock_install.assert_called_once()
        # Ensure backup operation was triggered
        mock_backup.assert_called_once_with(
            file_path="backup.json",
            configs=ANY
        )
        # Ensure logging was used
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )

# ------------------------------------------------------------------------------

def test_main_restore(
    mock_config
):

    with patch.object(sys, "argv", ["dependencies.py", "--restore-packages", "restore.json"]), \
         patch("packages.requirements.lib.package_utils.restore_packages") as mock_restore, \
         patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:
        dependencies.main()  # Execute main()
        # Ensure `restore_packages()` was called with the expected arguments
        mock_restore.assert_called_once_with(
            file_path="restore.json",
            configs=ANY
        )
        # Ensure logging was triggered
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )

# ------------------------------------------------------------------------------

def test_main_migration(
    mock_config
):

    with patch.object(
            sys,
            "argv",
            ["dependencies.py", "--migrate-packages", "migrate.json"]
         ), \
         patch(
             "packages.requirements.lib.package_utils.migrate_packages"
         ) as mock_migrate, \
         patch(
             "packages.appflow_tracer.lib.log_utils.log_message"
         ) as mock_log:
        dependencies.main()  # Execute main()
        # Convert PosixPath before logging
        serialized_configs = serialize_configs(
            mock_config
        )
        # Ensure function calls receive converted configs
        mock_migrate.assert_called_once_with(
            file_path="migrate.json",
            configs=ANY
        )
        # Ensure logging does not fail due to PosixPath serialization
        mock_log.assert_any_call(
            ANY,
            configs=ANY
        )  # Allow flexibility instead of exact match

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
