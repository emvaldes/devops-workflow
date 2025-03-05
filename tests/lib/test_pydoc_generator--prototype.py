#!/usr/bin/env python3

# File: ./tests/lib/test_pydoc_generator.py
__version__ = "0.1.1"  ## Updated test suite version

"""
File: tests/lib/test_pydoc_generator.py

Description:
    Unit tests for `lib/pydoc_generator.py`.

    This module contains unit tests to validate the core functionality of the PyDoc generator.
    It ensures that:
    - Documentation is correctly generated for Python modules.
    - Output directories are properly structured.
    - Errors and failures are logged as expected.

Improvements:
    - **Path Handling**: Uses `tmp_path` fixture to avoid hardcoded paths.
    - **Better Mocks & Assertions**: Ensures calls are precise and validated properly.
    - **Coverage & Documentation Verification**: Confirms expected files are written.

Dependencies:
    - pytest
    - unittest.mock
    - pathlib
    - shutil

Usage:
    Run the tests using:
    ```bash
    pytest -v tests/lib/test_pydoc_generator.py
    ```
"""

import sys
import pytest
import shutil
import subprocess

from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lib import pydoc_generator

@pytest.fixture
def mock_configs():
    """
    Provides a mock `CONFIGS` dictionary for tests.

    Returns:
        dict: A mock configuration dictionary with logging and tracing disabled.
    """
    return {
        "logging": {
            "enable": False,
            "module_name": "test_pydoc_generator",
            "package_name": "lib"  # <-- Add this line to prevent KeyError
        },
        "tracing": {"enable": False},
    }

@pytest.fixture
def temp_doc_dir(tmp_path):
    """
    Creates a temporary directory for storing generated documentation.

    Args:
        tmp_path (Path): A pytest fixture providing a unique temporary directory.

    Returns:
        Path: The path to the temporary documentation directory.
    """
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir


def test_create_structure(tmp_path):
    """
    Test that `create_structure()` properly creates documentation directories.

    Verifies:
        - The function returns the correct path.
        - The directory is created as expected.
    """
    base_path = tmp_path / "mock_docs"
    package_name = Path("mock_package")

    result = pydoc_generator.create_structure(base_path, package_name)

    assert result == base_path / package_name
    assert result.exists()
    assert result.is_dir()


def test_generate_pydoc(tmp_path, mock_configs):
    """
    Test that `generate_pydoc()` executes correctly with valid file paths.

    Verifies:
        - `pydoc` runs successfully.
        - The output documentation file is created.
        - Coverage is generated.
    """
    project_path = tmp_path / "mock_project"
    project_path.mkdir(parents=True, exist_ok=True)

    file_path = project_path / "test_module.py"
    file_path.write_text("def mock_function(): pass")

    docs_path = tmp_path / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)  # Ensure the docs directory exists

    with patch("lib.pydoc_generator.subprocess.check_output", return_value="Mock documentation output"), \
         patch("lib.pydoc_generator.log_utils.log_message"):

        pydoc_generator.generate_pydoc(project_path, file_path, docs_path, mock_configs)

    # Verify output file exists
    output_doc_file = docs_path / f"{file_path.stem}.pydoc"
    assert output_doc_file.exists(), "Documentation file was not created"

    # Verify content exists
    assert output_doc_file.read_text().strip(), "Documentation file is empty"

def test_generate_pydoc_handles_error(tmp_path, mock_configs):
    """
    Test that `generate_pydoc()` handles subprocess errors properly.

    Verifies:
        - Logs an error message when `pydoc` fails.
        - Creates an error log file.
    """
    project_path = tmp_path / "mock_project"
    project_path.mkdir(parents=True, exist_ok=True)

    file_path = project_path / "test_module.py"
    file_path.write_text("def mock_function(): pass")

    docs_path = tmp_path / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)  # Ensure docs directory exists

    with patch("lib.pydoc_generator.subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "pydoc")), \
         patch("lib.pydoc_generator.log_utils.log_message") as mock_log:

        pydoc_generator.generate_pydoc(project_path, file_path, docs_path, mock_configs)

    error_file = docs_path / f"{file_path.stem}.pydoc.error"
    assert error_file.exists(), "Error log file was not created"
    assert error_file.read_text().strip(), "Error log file is empty"
    mock_log.assert_called()

def test_generate_report(tmp_path, mock_configs):
    """
    Test that `generate_report()` correctly produces a coverage summary.

    Verifies:
        - `coverage report` executes without error.
        - Coverage summary file is created.
    """
    coverage_report = tmp_path / "coverage.report"

    with patch("lib.pydoc_generator.subprocess.run") as mock_run, \
         patch("lib.pydoc_generator.log_utils.log_message"):

        pydoc_generator.generate_report(coverage_report, mock_configs)

    # Ensure the report file is created
    assert coverage_report.exists(), "Coverage report file was not created"

    # Ensure subprocess was called correctly
    mock_run.assert_called_once()
    mock_run_args, mock_run_kwargs = mock_run.call_args

    assert mock_run_args[0] == ["python", "-m", "coverage", "report"], "Unexpected command executed"
    assert mock_run_kwargs["stderr"] == subprocess.PIPE, "Unexpected stderr parameter"
    assert mock_run_kwargs["text"] is True, "Unexpected text parameter"
    assert mock_run_kwargs["check"] is True, "Unexpected check parameter"

def test_create_pydocs(tmp_path, mock_configs):
    """
    Test that `create_pydocs()` processes multiple files correctly.
    """
    project_path = tmp_path / "mock_project"
    project_path.mkdir(parents=True, exist_ok=True)

    file1 = project_path / "module1.py"
    file2 = project_path / "module2.py"

    file1.write_text("def mock_function(): pass")
    file2.write_text("def another_function(): pass")

    docs_path = tmp_path / "docs"

    with patch("lib.pydoc_generator.create_structure") as mock_create_structure, \
         patch("lib.pydoc_generator.generate_pydoc") as mock_generate_pydoc:

        pydoc_generator.create_pydocs(project_path, docs_path, [file1, file2], mock_configs)

    print("\n--- DEBUG: mock_create_structure calls ---")
    for call in mock_create_structure.call_args_list:
        print(call)

    # Verify `create_structure()` was called with the correct relative package names
    for file in [file1, file2]:
        relative_dir = str(file.parent.relative_to(project_path))
        expected_package_name = relative_dir if relative_dir else "."

        # Corrected validation
        assert any(
            call.kwargs == {"base_path": docs_path, "package_name": expected_package_name}
            for call in mock_create_structure.call_args_list
        ), f"Expected call to create_structure({docs_path}, {expected_package_name}) not found."
