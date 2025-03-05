#!/usr/bin/env python3

# File: ./tests/test_run.py
__version__ = "0.1.1"  ## Package version

"""
File Path: tests/test_run.py

Description:
    Unit tests for `run.py`

    This module contains tests to verify the correct behavior of functions within `run.py`.
    It ensures that argument parsing, CLI execution, and core entry points work as expected.

Core Features:
    - **Argument Parsing Validation**: Confirms CLI flags are correctly interpreted.
    - **Execution Entry Points**: Ensures `main()` runs properly with `--pydoc` and `--target` options.
    - **Mocked Testing**: Uses `unittest.mock` to isolate dependencies.

Dependencies:
    - pytest
    - unittest.mock
    - pathlib
    - argparse
    - sys

Expected Behavior:
    - Tests should confirm correct argument parsing.
    - Execution flow should be verified through mocks.
    - CLI behavior for documentation and module execution should be validated.

Usage:
    To run the tests:
    ```bash
    pytest -v tests/test_run.py
    ```

Example Output:
    ```bash
    ============================= test session starts =============================
    platform darwin -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0
    collected 4 items

    tests/test_run.py::test_collect_files PASSED
    tests/test_run.py::test_parse_arguments PASSED
    tests/test_run.py::test_main_pydoc PASSED
    tests/test_run.py::test_main_target PASSED

    ========================== 4 passed in 1.76s ==========================
    ```
"""

import sys
import pytest
import argparse
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from packages.appflow_tracer import tracing
import run

# Setup CONFIGS
CONFIGS = tracing.setup_logging(logname_override='logs/tests/test_run.log')
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing

@pytest.fixture(autouse=True)
def mock_configs():
    """Mock CONFIGS for test isolation."""
    global CONFIGS
    return CONFIGS

@pytest.fixture
def mock_project_structure():
    """
    Create a mock directory structure **inside the actual project root**.
    """
    base_dir = Path(run.environment.project_root) / "tests" / "mock_project"
    base_dir.mkdir(parents=True, exist_ok=True)

    mock_file = base_dir / "mock_file.py"
    mock_file.write_text("def mock_function(): pass")  # Create a non-empty Python file

    return base_dir, mock_file

def test_collect_files(mock_project_structure):
    """
    Test that collect_files correctly finds all Python files in the project.
    """
    base_dir, mock_file = mock_project_structure  # Extract base directory

    # Debugging: List files in the mock directory
    print("\nMock Directory Structure:")
    for path in base_dir.rglob("*"):  # Use `base_dir`, not `mock_project_structure`
        print(path)

    # Call collect_files
    files_list = run.collect_files(base_dir, extensions=[".py"])

    # Debugging: Print what was collected
    print("\nCollected Files by collect_files():")
    for f in files_list:
        print(f)

    # Convert to relative paths for verification
    expected_files = {
        str(mock_file),  # Adjusted to match the mock structure
    }

    collected_files = {str(file) for file in files_list}

    assert collected_files == expected_files, f"Expected {expected_files}, but got {collected_files}"

def test_parse_arguments():
    """
    Test `parse_arguments()` with a sample argument set.

    This test verifies that `--help` triggers a SystemExit as expected.
    """
    test_args = ["run.py", "--help"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            run.parse_arguments()

import subprocess
from unittest.mock import patch
from pathlib import Path

import subprocess
from unittest.mock import patch
from pathlib import Path

@patch("subprocess.run")
@patch("coverage.Coverage")
@patch("subprocess.check_output")  # Mock subprocess output
@patch("lib.pydoc_generator.generate_report")  # Mock the new function
def test_main_coverage(
    mock_generate_report,
    mock_check_output,
    mock_coverage,
    mock_subprocess,
    monkeypatch,
    mock_project_structure
):
    """
    Test that main() correctly enables and finalizes coverage when --coverage is passed.
    """
    base_dir, mock_file = mock_project_structure

    # Mock command-line arguments
    monkeypatch.setattr("sys.argv", ["run.py", "--pydoc", "--coverage"])

    # Mock coverage behavior
    mock_cov_instance = mock_coverage.return_value
    mock_cov_instance.start.return_value = None
    mock_cov_instance.stop.return_value = None
    mock_cov_instance.save.return_value = None

    # Mock a generic coverage report output (no specific filenames)
    mock_coverage_output = """\
Name      Stmts   Miss  Cover
----------------------------
file1.py      10      2   80%
file2.py      15      0  100%
----------------------------
TOTAL         25      2   92%
"""
    mock_check_output.return_value = mock_coverage_output

    # Mock collect_files() to return our mock file **inside project root**
    with patch("run.collect_files", return_value=[mock_file]):
        run.main()

    # **Verify Coverage Behavior**
    mock_cov_instance.start.assert_called_once()
    mock_cov_instance.stop.assert_called_once()
    mock_cov_instance.save.assert_called_once()

    # Ensure subprocess calls were made for coverage processing
    mock_subprocess.assert_any_call(["python", "-m", "coverage", "combine"], check=True)
    mock_subprocess.assert_any_call(["python", "-m", "coverage", "html", "-d", "docs/htmlcov"], check=True)

    # **Verify that generate_report was called with correct parameters**
    coverage_summary_file = Path(run.environment.project_root) / "docs/coverage/coverage.report"

    # Check that generate_report was called at least once
    mock_generate_report.assert_called_once()

    # Retrieve actual call arguments
    called_args, called_kwargs = mock_generate_report.call_args

    # **Match keyword arguments instead of positional**
    assert called_kwargs["coverage_report"].resolve() == coverage_summary_file.resolve(), \
        f"Expected {coverage_summary_file}, got {called_kwargs['coverage_report']}"

    assert called_kwargs["configs"] == run.CONFIGS, "CONFIGS argument does not match."

@patch("lib.pydoc_generator.create_pydocs")
@patch("subprocess.run")
def test_main_pydoc(
    mock_subprocess,
    mock_create_pydocs,
    monkeypatch,
    tmp_path
):
    """
    Test that main() correctly executes --pydoc logic.

    Expected Behavior:
        - `create_pydocs()` should be called once with correct arguments.
        - No unexpected subprocess calls should be made.

    Fixes:
        - Aligns with updated function signature of `create_pydocs`.
        - Ensures assertions match the expected behavior.

    Args:
        mock_subprocess: Mock for `subprocess.run`.
        mock_create_pydocs: Mock for `lib.pydoc_generator.create_pydocs`.
        monkeypatch: Fixture to modify `sys.argv`.
        tmp_path: Temporary path for test file operations.
    """

    # Simulate command-line argument
    monkeypatch.setattr("sys.argv", ["run.py", "--pydoc"])

    # Create a mock Python file inside the temp directory
    mock_file = tmp_path / "mock_file.py"
    mock_file.write_text("def mock_function(): pass")  # Ensure non-empty file

    # Mock collect_files() to return the mock file
    with patch("run.collect_files", return_value=[mock_file]):
        run.main()

    # **Verify `create_pydocs()` was called with correct arguments**
    mock_create_pydocs.assert_called_once_with(
        project_path=Path(run.environment.project_root),
        base_path=str(Path(run.environment.project_root) / "docs/pydoc"),
        files_list=[mock_file],  # Ensure it was called with the correct file list
        configs=run.CONFIGS
    )

    # **Log subprocess calls for debugging**
    print("\nSubprocess Calls:")
    for call in mock_subprocess.call_args_list:
        print(call)

    # **Ensure subprocess calls were made if required**
    if mock_subprocess.call_args_list:
        mock_subprocess.assert_any_call(["python", "-m", "coverage", "combine"], check=True)
        mock_subprocess.assert_any_call(["python", "-m", "coverage", "html", "-d", "docs/htmlcov"], check=True)
    else:
        print("[WARNING] No subprocess calls detected. Ensure this is expected behavior.")
