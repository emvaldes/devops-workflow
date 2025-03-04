#!/usr/bin/env python3

# File: ./tests/test_run.py
__version__ = "0.1.0"  ## Package version

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
    collected 3 items

    tests/test_run.py::test_parse_arguments PASSED
    tests/test_run.py::test_main_pydoc PASSED
    tests/test_run.py::test_main_target PASSED

    ========================== 3 passed in 1.76s ==========================
    ```
"""

import sys
import pytest
import argparse
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]  # Adjust as needed
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
    """
    Globally mock CONFIGS for all tests.

    This ensures that logging and tracing remain disabled during testing.
    """
    global CONFIGS
    return CONFIGS

def test_parse_arguments():
    """
    Test `parse_arguments()` with a sample argument set.

    This test verifies that `--help` triggers a SystemExit as expected.
    """
    test_args = ["run.py", "--help"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            run.parse_arguments()

def test_main_pydoc():
    """
    Test `main()` when `--pydoc` is passed.

    Expected Behavior:
        - `pydoc_engine.create_pydocs()` should be invoked.
    """
    with patch("run.parse_arguments") as mock_parse_args, \
         patch("run.pydoc_engine.create_pydocs") as mock_create_pydocs:

        mock_parse_args.return_value.pydoc = True
        run.main()
        mock_create_pydocs.assert_called()

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
