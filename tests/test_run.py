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
def mock_project_structure(tmp_path):
    """
    Create a mock directory structure for testing collect_files().
    """
    base_dir = tmp_path / "mock_project"
    base_dir.mkdir()

    (base_dir / "scripts").mkdir()
    (base_dir / "lib").mkdir()

    # Create sample non-empty Python files
    (base_dir / "run.py").write_text("#!/usr/bin/env python3\n")
    (base_dir / "scripts" / "script1.py").write_text("print('Hello')")
    (base_dir / "scripts" / "script2.py").write_text("print('World')")
    (base_dir / "lib" / "module1.py").write_text("def foo(): pass")
    (base_dir / "lib" / "module2.py").write_text("def bar(): pass")

    return base_dir

def test_collect_files(mock_project_structure):
    """
    Test that collect_files correctly finds all Python files in the project.
    """
    project_path = mock_project_structure

    # Debugging: List files in the mock directory
    print("\nMock Directory Structure:")
    for path in project_path.rglob("*"):
        print(path)

    # Call collect_files
    files_list = run.collect_files(project_path, extensions=[".py"])

    # Debugging: Print what was collected
    print("\nCollected Files by collect_files():")
    for f in files_list:
        print(f)

    # Convert to relative paths for verification
    expected_files = {
        str(mock_project_structure / "run.py"),
        str(mock_project_structure / "scripts" / "script1.py"),
        str(mock_project_structure / "scripts" / "script2.py"),
        str(mock_project_structure / "lib" / "module1.py"),
        str(mock_project_structure / "lib" / "module2.py"),
    }

    collected_files = {str(file) for file in files_list}

    assert collected_files == expected_files, "collect_files did not return the expected files"

def test_parse_arguments():
    """
    Test `parse_arguments()` with a sample argument set.

    This test verifies that `--help` triggers a SystemExit as expected.
    """
    test_args = ["run.py", "--help"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            run.parse_arguments()

@patch("lib.pydoc_generator.create_pydocs")
@patch("subprocess.run")
def test_main_pydoc(mock_subprocess, mock_create_pydocs, monkeypatch, tmp_path):
    """
    Test that main() correctly executes --pydoc logic.
    """
    # Simulate command-line argument
    monkeypatch.setattr("sys.argv", ["run.py", "--pydoc"])

    # Mock return value for collect_files
    mock_files_list = [tmp_path / "mock_file.py"]
    with patch("run.collect_files", return_value=mock_files_list):
        run.main()

    # Ensure create_pydocs was called with correct arguments
    mock_create_pydocs.assert_called_once()

    # Log all subprocess calls for debugging
    print("\nSubprocess Calls:")
    for call in mock_subprocess.call_args_list:
        print(call)

    # Print captured subprocess calls for debugging
    print("\nCaptured Subprocess Calls:")
    print(mock_subprocess.call_args_list)

    # Ensure subprocess coverage commands were executed
    assert mock_subprocess.call_args_list, "No subprocess calls were made"

    mock_subprocess.assert_any_call(["python", "-m", "coverage", "combine"], check=True)
    mock_subprocess.assert_any_call(["python", "-m", "coverage", "html", "-d", "docs/htmlcov"], check=True)

def test_main_target():
    """
    Test `main()` when `--target` is passed.

    Expected Behavior:
        - `subprocess.run()` should be called with the correct module.
    """
    with patch("run.parse_arguments") as mock_parse_args, \
         patch("run.subprocess.run") as mock_subprocess:

        mock_parse_args.return_value.pydoc = False
        mock_parse_args.return_value.target = "some_module"
        run.main()
        mock_subprocess.assert_called_with([sys.executable, "-m", "some_module"])
