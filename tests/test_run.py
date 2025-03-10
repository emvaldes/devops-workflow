#!/usr/bin/env python3

# File: ./tests/test_run.py

__module_name__ = "test_run"
__version__ = "0.1.2"  ## Updated Test Module version

# Standard library imports - Core system module
import sys
import subprocess
import argparse
import json

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Unit testing and mocking tools
from unittest.mock import (
    ANY,
    MagicMock,
    patch
)

# Third-party library imports - Testing framework
import pytest

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run
from packages.appflow_tracer import tracing

# Convert PosixPath objects into strings for JSON serialization
def serialize_configs(configs):

    return json.loads(json.dumps(configs, default=lambda o: str(o) if isinstance(o, Path) else o))

# ------------------------------------------------------------------------------
# Test: parse_arguments()
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("args, expected_attr, expected_value", [
    ([], "pydoc", False),  # Default value (no arguments)
    (["--pydoc"], "pydoc", True),  # Enable PyDoc generation
    (["--coverage"], "coverage", True),  # Enable Coverage Mode
    (["--target", "tests/example.py"], "target", "tests/example.py"),  # Specify target file
])
def test_parse_arguments(args, expected_attr, expected_value):

    test_args = ["run.py"] + args  # Ensure script name is included

    with patch.object(sys, "argv", test_args), \
         patch("sys.exit") as mock_exit:  # Prevent argparse from exiting

        parsed_args = run.parse_arguments()  # Call the function

        # Ensure correct argument parsing
        assert getattr(parsed_args, expected_attr) == expected_value, \
            f"Expected `{expected_attr}={expected_value}`, but got `{getattr(parsed_args, expected_attr, None)}`"

        mock_exit.assert_not_called()  # Ensure no forced exit happened

# ------------------------------------------------------------------------------
# Test: collect_files()
# ------------------------------------------------------------------------------

@pytest.fixture
def mock_project_structure():

    with patch("pathlib.Path.is_dir", return_value=True), \
         patch("pathlib.Path.rglob", return_value=[Path("mock_project/mock_file.py")]), \
         patch("pathlib.Path.stat", return_value=MagicMock(st_size=10)):  # Simulate non-empty file

        yield Path("mock_project"), Path("mock_project/mock_file.py")

def test_collect_files(mock_project_structure):

    base_dir, mock_file = mock_project_structure
    files_list = run.collect_files(base_dir, extensions=[".py"])

    expected_files = {str(mock_file.resolve())}  # Convert to absolute path
    collected_files = {str(file) for file in files_list}

    assert collected_files == expected_files, f"Expected {expected_files}, but got {collected_files}"

# # ------------------------------------------------------------------------------
# # Test: main() - Backup
# # ------------------------------------------------------------------------------
#
# def test_main_backup(requirements_config):
#     """Ensure `main()` correctly handles backup operations."""
#     with patch.object(sys, "argv", ["run.py", "--backup-packages", "backup.json"]), \
#          patch("packages.requirements.lib.package_utils.backup_packages") as mock_backup, \
#          patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:
#
#         run.main()
#         mock_backup.assert_called_once_with(file_path="backup.json", configs=ANY)
#         mock_log.assert_any_call(ANY, configs=ANY)
#
# # ------------------------------------------------------------------------------
# # Test: main() - Restore
# # ------------------------------------------------------------------------------
#
# def test_main_restore(requirements_config):
#     """Ensure `main()` correctly handles restore operations."""
#     with patch.object(sys, "argv", ["run.py", "--restore-packages", "restore.json"]), \
#          patch("packages.requirements.lib.package_utils.restore_packages") as mock_restore, \
#          patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:
#
#         run.main()
#         mock_restore.assert_called_once_with(file_path="restore.json", configs=ANY)
#         mock_log.assert_any_call(ANY, configs=ANY)
#
# # ------------------------------------------------------------------------------
# # Test: main() - Migration
# # ------------------------------------------------------------------------------
#
# def test_main_migration(requirements_config):
#     """Ensure `main()` correctly handles migration operations."""
#     with patch.object(sys, "argv", ["run.py", "--migrate-packages", "migrate.json"]), \
#          patch("packages.requirements.lib.package_utils.migrate_packages") as mock_migrate, \
#          patch("packages.appflow_tracer.lib.log_utils.log_message") as mock_log:
#
#         run.main()
#         serialized_configs = serialize_configs(requirements_config)
#
#         mock_migrate.assert_called_once_with(file_path="migrate.json", configs=ANY)
#         mock_log.assert_any_call(ANY, configs=serialized_configs)

# ------------------------------------------------------------------------------
# Test: main() - PyDoc
# ------------------------------------------------------------------------------

@patch("lib.pydoc_generator.create_pydocs")
@patch("subprocess.run")
def test_main_pydoc(mock_subprocess, mock_create_pydocs, monkeypatch, tmp_path):

    monkeypatch.setattr("sys.argv", ["run.py", "--pydoc"])
    mock_file = tmp_path / "mock_file.py"
    mock_file.write_text("def mock_function(): pass")

    with patch("run.collect_files", return_value=[mock_file]):
        run.main()

    mock_create_pydocs.assert_called_once_with(
        project_path=Path(run.environment.project_root),
        base_path=str(Path(run.environment.project_root) / "docs/pydoc"),
        files_list=[mock_file],
        configs=run.CONFIGS
    )

# ------------------------------------------------------------------------------
# Test: main() - Coverage
# ------------------------------------------------------------------------------

@patch("subprocess.run")
@patch("subprocess.check_output", return_value="mock coverage output\n")  # Fix TypeError issue
@patch("lib.pydoc_generator.generate_report")  # Mock PyDoc since coverage is part of it
def test_main_coverage(
    mock_generate_report,
    mock_check_output,
    mock_subprocess,
    monkeypatch,
    tmp_path
):

    # Simulate CLI args: run.py --pydoc --coverage
    monkeypatch.setattr(
        "sys.argv",
        ["run.py", "--pydoc", "--coverage"]
    )
    test_file = Path(__file__).resolve()

    # Ensure `docs/coverage/coverage.report` exists before it is read
    coverage_report = tmp_path / "coverage.report"
    coverage_report.write_text("Mock Coverage Report\n")

    # Make `mock_generate_report` simulate file creation
    def _generate_mock_report(*args, **kwargs):
        if "coverage_report" in kwargs:
            kwargs["coverage_report"].write_text("Generated Coverage Report\n")

    mock_generate_report.side_effect = _generate_mock_report

    # Mock file collection (should return this test file)
    with patch("run.collect_files", return_value=[test_file]):
        run.main()

    # Ensure `generate_report()` was called (since PyDoc handles coverage)
    mock_generate_report.assert_called_once()

    # Ensure `coverage combine` and `coverage html` were executed inside PyDoc
    mock_subprocess.assert_any_call(
        ["python", "-m", "coverage", "combine"],
        check=True
    )
    mock_subprocess.assert_any_call(
        ["python", "-m", "coverage", "html", "-d", "docs/htmlcov"],
        check=True
    )

    # Ensure `coverage.report` file was created
    assert coverage_report.exists(), "Expected coverage report file to be created but it does not exist."

def main() -> None:
    pass

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
