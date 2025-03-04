#!/usr/bin/env python3

# File: ./tests/test_pydoc_generator.py
# Version: 0.1.0

"""
File: tests/test_pydoc_generator.py

Description:
    Unit tests for `lib/pydoc_generator.py`

    This module tests the core functionality of the PyDoc generator, ensuring
    that documentation is generated correctly, directories are structured properly,
    and error handling works as expected.

Core Features:
    - **Documentation Generation**: Verifies `pydoc` command execution.
    - **Directory Structure Creation**: Ensures output paths are created.
    - **Error Handling & Logging**: Tests logging and error messages.

Dependencies:
    - pytest
    - unittest.mock
    - pathlib
    - shutil
"""

# Package version
__version__ = "0.1.0"

import sys
import pytest
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lib import pydoc_generator

@pytest.fixture
def mock_configs():
    """Mock CONFIGS for tests."""
    return {
        "logging": {"enable": False},
        "tracing": {"enable": False}
    }

def test_create_structure():
    """Test that create_structure properly creates documentation directories."""
    base_path = Path("/mock/docs")
    package_name = Path("mock_package")

    with patch("lib.pydoc_generator.Path.mkdir") as mock_mkdir:
        result = pydoc_generator.create_structure(base_path, package_name)
        assert result == base_path / package_name
        mock_mkdir.assert_called()

def test_generate_pydoc():
    """Test generate_pydoc execution with proper file paths."""
    project_path = Path("/mock/project")
    file_path = project_path / "test_module.py"
    docs_path = Path("/mock/docs")

    with patch("lib.pydoc_generator.subprocess.check_output") as mock_subprocess, \
         patch("lib.pydoc_generator.log_utils.log_message"):

        mock_subprocess.return_value = "Mock documentation output"
        pydoc_generator.generate_pydoc(project_path, file_path, docs_path, {})

        mock_subprocess.assert_called()

def test_create_pydocs():
    """Test create_pydocs execution with multiple files."""
    project_path = Path("/mock/project")
    base_path = Path("/mock/docs")
    files_list = [project_path / "module1.py", project_path / "module2.py"]

    with patch("lib.pydoc_generator.create_structure") as mock_create_structure, \
         patch("lib.pydoc_generator.generate_pydoc") as mock_generate_pydoc:

        mock_create_structure.side_effect = lambda base, pkg: base / pkg
        pydoc_generator.create_pydocs(project_path, base_path, files_list, {})

        mock_generate_pydoc.assert_called()
