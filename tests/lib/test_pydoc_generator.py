#!/usr/bin/env python3

# File: ./tests/lib/test_pydoc_generator.py
__version__ = "0.1.1"  ## Updated test suite version

#-------------------------------------------------------------------------------

# Standard library imports - Core system modules
import sys
import subprocess
import shutil

# Standard library imports - File system-related module
from pathlib import Path  # For handling paths in tests

# Standard library imports - Unit testing and mocking tools
from unittest.mock import (
    patch,
    MagicMock
)  # Used for test isolation and function patching

# Third-party library imports - Testing framework
import pytest  # PyTest framework for unit testing

#-------------------------------------------------------------------------------

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

#-------------------------------------------------------------------------------

from lib import pydoc_generator

#-------------------------------------------------------------------------------

@pytest.fixture
def mock_configs():

    return {
        "logging": {
            "enable": False,
            "module_name": "test_pydoc_generator",
            "package_name": "lib"  # <-- Add this line to prevent KeyError
        },
        "tracing": {"enable": False},
    }

#-------------------------------------------------------------------------------

@pytest.fixture
def temp_doc_dir(
    tmp_path
):

    doc_dir = tmp_path / "docs"
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir

def test_create_structure(
    tmp_path
):

    base_path = tmp_path / "mock_docs"
    package_name = Path("mock_package")
    result = pydoc_generator.create_structure(base_path, package_name)
    assert result == base_path / package_name
    assert result.exists()
    assert result.is_dir()

#-------------------------------------------------------------------------------

def test_generate_pydoc(
    tmp_path,
    mock_configs
):

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

#-------------------------------------------------------------------------------

def test_generate_pydoc_handles_error(
    tmp_path,
    mock_configs
):

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

#-------------------------------------------------------------------------------

def test_generate_report(
    tmp_path,
    mock_configs
):

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

#-------------------------------------------------------------------------------

def test_create_pydocs(
    tmp_path,
    mock_configs
):

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

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
