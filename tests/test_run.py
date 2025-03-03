#!/usr/bin/env python3

"""
Unit tests for run.py

This module contains tests for verifying the correct behavior of functions in run.py.
It ensures that argument parsing, documentation generation, and execution entry points function correctly.
"""

import sys
import pytest
import logging
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust as needed
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
    """Globally mock CONFIGS for all tests."""
    global CONFIGS
    return CONFIGS

@pytest.fixture
def mock_logger() -> MagicMock:
    """Create a mock logger for testing purposes."""
    logger = MagicMock(spec=logging.Logger)
    logger.handlers = []  # Ensure handlers attribute exists
    return logger

def test_create_doc_structure():
    """Test that create_doc_structure runs without errors."""
    with patch("run.os.makedirs") as mock_makedirs:
        run.create_doc_structure("/mock/path", "mock_package")
        mock_makedirs.assert_called()

def test_generate_pydoc():
    """Test generate_pydoc function using run.py as the target."""
    docs_mock_path = Path(ROOT_DIR) / "docs/mocks"
    docs_mock_path.mkdir(parents=True, exist_ok=True)

    try:
        with patch("run.subprocess.run") as mock_subprocess, \
             patch("run.log_utils.log_message"), \
             patch("run.environment.category.debug.id", new=MagicMock()), \
             patch("run.CONFIGS", CONFIGS, create=True):

            mock_subprocess.return_value.stdout = "Mock pydoc output"  # Ensure stdout is a valid string
            file_path = Path("run.py").resolve()  # Target run.py
            run.generate_pydoc(file_path, str(docs_mock_path))
            mock_subprocess.assert_called()
    finally:
        shutil.rmtree(docs_mock_path)  # Ensure cleanup after test

def test_scan_and_generate_docs():
    """Test scan_and_generate_docs function execution."""
    with patch("run.generate_pydoc") as mock_generate_pydoc, \
         patch("run.log_utils.log_message"), \
         patch("run.environment.category.debug.id", new=MagicMock()), \
         patch("run.CONFIGS", CONFIGS, create=True), \
         patch("run.os.walk") as mock_os_walk:

        # Simulate found Python files
        mock_os_walk.return_value = [("/mock/scan_path", [], ["test.py", "module.py"])]
        mock_generate_pydoc.side_effect = lambda *args, **kwargs: None  # Ensure function executes
        run.scan_and_generate_docs("/mock/scan_path", "/mock/base_doc")
        mock_generate_pydoc.assert_called()

def test_parse_arguments():
    """Test parse_arguments function with sample arguments."""
    test_args = ["run.py", "--help"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            run.parse_arguments()

def test_main():
    """Test main function execution."""
    with patch("run.parse_arguments") as mock_parse_args, \
         patch("run.scan_and_generate_docs") as mock_scan_docs:

        mock_parse_args.return_value = MagicMock()
        run.main()
        mock_scan_docs.assert_called()
