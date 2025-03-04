#!/usr/bin/env python3

# File: ./tests/lib/test_pydoc_generator.py
# Version: 0.1.2

"""
File: tests/lib/test_pydoc_generator.py

Description:
    Unit tests for `lib/pydoc_generator.py`.

    This module contains unit tests to validate the core functionality of the PyDoc generator.
    It ensures that:
    - Documentation is correctly generated for Python modules.
    - Output directories are properly structured.
    - Errors and failures are logged as expected.

Core Features:
    - **Documentation Generation**: Verifies `pydoc` command execution.
    - **Directory Structure Creation**: Ensures that documentation paths are generated correctly.
    - **Error Handling & Logging**: Ensures graceful failure handling and proper logging.

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
    Fixture to provide a mock `CONFIGS` dictionary for tests.

    Returns:
        dict: A mock configuration dictionary with logging and tracing disabled.
    """

    return {
        "logging": {
            "enable": False,
            "package_name": __package__,  # Use the actual package name
            "module_name": "test_pydoc_generator",
        },
        "tracing": {"enable": False}
    }

@pytest.fixture
def temp_doc_dir(
    tmp_path
):
    """
    Fixture to create a temporary directory for storing generated documentation.

    Args:
        tmp_path (Path): A pytest fixture providing a unique temporary directory.

    Returns:
        Path: The path to the temporary documentation directory.
    """

    doc_dir = tmp_path / "docs"
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir

def test_create_structure():
    """
    Test that `create_structure` properly creates documentation directories.

    This test ensures that the function correctly creates the expected directory
    structure for storing PyDoc documentation.

    Assertions:
        - The function returns the correct path.
        - The `mkdir` method is called to create the directory.
    """
    base_path = Path("/mock/docs")
    package_name = Path("mock_package")

    with patch("lib.pydoc_generator.Path.mkdir") as mock_mkdir:
        result = pydoc_generator.create_structure(base_path, package_name)
        assert result == base_path / package_name
        mock_mkdir.assert_called()

def test_generate_pydoc(
    mock_configs,
    temp_doc_dir
):
    """
    Test that `generate_pydoc` executes correctly with valid file paths.

    This test verifies:
        - `pydoc` runs without errors.
        - The subprocess call is correctly constructed and executed.

    Args:
        mock_configs (dict): The mocked logging and tracing configuration.
        temp_doc_dir (Path): Temporary directory for storing generated docs.
    """

    project_path = Path("/mock/project")
    file_path = project_path / "test_module.py"

    with patch("lib.pydoc_generator.subprocess.check_output") as mock_subprocess, \
         patch("lib.pydoc_generator.log_utils.log_message"):

        mock_subprocess.return_value = "Mock documentation output"
        pydoc_generator.generate_pydoc(project_path, file_path, temp_doc_dir, mock_configs)

        mock_subprocess.assert_called()

def test_generate_pydoc_handles_error(
    mock_configs,
    temp_doc_dir
):
    """
    Test that `generate_pydoc` handles errors gracefully.

    This test verifies:
        - The function catches `subprocess.CalledProcessError`.
        - Error messages are logged correctly.

    Args:
        mock_configs (dict): The mocked logging and tracing configuration.
        temp_doc_dir (Path): Temporary directory for storing generated docs.
    """

    project_path = Path("/mock/project")
    file_path = project_path / "test_module.py"

    with patch("lib.pydoc_generator.subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "pydoc")), \
         patch("lib.pydoc_generator.log_utils.log_message") as mock_log:

        pydoc_generator.generate_pydoc(project_path, file_path, temp_doc_dir, mock_configs)
        mock_log.assert_called()

def test_create_pydocs(
    mock_configs,
    temp_doc_dir
):
    """
    Test that `create_pydocs` processes multiple files correctly.

    This test ensures:
        - Documentation is created for multiple Python files.
        - The directory structure is properly managed.
        - The `generate_pydoc` function is invoked as expected.

    Args:
        mock_configs (dict): The mocked logging and tracing configuration.
        temp_doc_dir (Path): Temporary directory for storing generated docs.
    """

    project_path = Path("/mock/project")
    files_list = [project_path / "module1.py", project_path / "module2.py"]

    with patch("lib.pydoc_generator.create_structure", side_effect=lambda base_path, package_name: base_path / package_name) as mock_create_structure, \
         patch("lib.pydoc_generator.generate_pydoc") as mock_generate_pydoc:

        pydoc_generator.create_pydocs(project_path, temp_doc_dir, files_list, mock_configs)
        mock_generate_pydoc.assert_called()
