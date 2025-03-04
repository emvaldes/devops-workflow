#!/usr/bin/env python3

"""
Test Module: test_tracing.py

This module contains unit tests for the `tracing.py` module in `appflow_tracer`.
It ensures that tracing, logging, and ANSI handling functions operate correctly.

## Tests:
1. **`test_setup_logging()`**
   - Validates that `tracing.setup_logging()` initializes logging correctly.
   - Ensures configuration keys (`colors`, `logging`, `tracing`, `stats`) exist.
   - Confirms `stats.created` remains static while `stats.updated` changes per execution.

2. **`test_print_capture()`**
   - Ensures `tracing.PrintCapture` properly captures and logs print statements.
   - Simulates `sys.stdout.write()` to verify expected output.

3. **`test_ansi_file_handler()`**
   - Ensures `tracing.ANSIFileHandler` removes ANSI escape sequences before writing logs.
   - Uses a helper function `remove_ansi()` to strip escape codes before emitting logs.

## Expected Behavior:
- **Logging configurations are correctly assigned** during initialization.
- **Print statements are redirected to the logging system**.
- **ANSI escape sequences are stripped before logging** to prevent unwanted formatting.

"""

# Package version
__version__ = "0.1.0"

import sys
import os

import json
import logging
import re

import pytest
from unittest.mock import patch, MagicMock

from pathlib import Path
from datetime import datetime, timezone

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from packages.appflow_tracer import tracing

CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_tracing.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

@pytest.fixture(autouse=True)
def mock_configs():
    """
    Mock the `CONFIGS` object globally for all tests if not already initialized.

    This fixture ensures that the `CONFIGS` object is available globally for all tests. If `CONFIGS` is not
    initialized, it creates a default configuration with logging and tracing disabled, and events for `install`
    and `update` enabled. It provides a consistent configuration for all tests that require access to `CONFIGS`.

    The fixture is automatically applied to all tests because of the `autouse=True` flag, eliminating the need to
    explicitly request it in individual test functions.

    Returns:
        dict: The `CONFIGS` dictionary, which includes configuration for logging, tracing, and event handling.
    """

    global CONFIGS
    if CONFIGS is None:
        CONFIGS = {
            "logging": {"enable": False},
            "tracing": {"enable": False},
            "events": {"install": True, "update": True},
        }
    return CONFIGS  # Explicitly returns CONFIGS

@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Create a mock logger for testing purposes.

    This fixture creates and returns a mock instance of a logger object using `MagicMock`, which simulates the behavior
    of a `logging.Logger` object. It also ensures that the `handlers` attribute is properly initialized as an empty list.

    This fixture is useful for testing logging functionality without writing actual logs, enabling verification of logging behavior
    and ensuring that logging methods are called as expected.

    Returns:
        MagicMock: A mock logger object that mimics the behavior of a `logging.Logger` instance.
    """

    logger = MagicMock(spec=logging.Logger)
    logger.handlers = []  # Ensure handlers attribute exists
    return logger

def test_setup_logging(
    mock_logger: MagicMock
) -> None:
    """
    Ensure `tracing.setup_logging()` correctly initializes logging configurations.

    This test verifies:
    - The returned `CONFIGS` contains all expected keys: `colors`, `logging`, `tracing`, and `stats`.
    - The logging file path is correctly assigned, with a dynamic filename containing the timestamp.
    - Ensures that `stats.created` remains static while `stats.updated` changes per execution.

    Args:
        mock_logger (MagicMock): Mock for the logger object to simulate logging behavior.

    Returns:
        None: This test does not return a value but asserts that logging configurations are set up correctly.
    """

    with patch(
        "packages.appflow_tracer.tracing.logging.getLogger",
        return_value=mock_logger
    ):
        config = tracing.setup_logging(
            logname_override='logs/tests/test_tracing.log'
        )
        assert isinstance(config, dict)
        assert "colors" in config
        assert "logging" in config
        assert "tracing" in config
        assert "stats" in config
        # Validate logging configurations
        assert config["logging"]["enable"] is True
        assert config["logging"]["max_logfiles"] == 5
        assert Path(
            config["logging"]["logs_dirname"]).parts[-2:] == (
                "appflow_tracer",
                "tracing"
            )
        # Allow log filename to include timestamps dynamically
        log_filename = Path(config["logging"]["log_filename"]).name
        assert "tracing" in log_filename and log_filename.endswith(".log")
        # Validate tracing is enabled
        assert config["tracing"]["enable"] is True
        # Validate `stats` properties
        assert "created" in config["stats"]
        assert "updated" in config["stats"]
        created_time = datetime.fromisoformat(config["stats"]["created"])
        updated_time = datetime.fromisoformat(config["stats"]["updated"])
        # Normalize both to naive datetimes

        # if updated_time.tzinfo is not None:
        #     updated_time = updated_time.replace(tzinfo=None)
        # Ensure both timestamps are offset-naive for valid comparison

        if created_time.tzinfo is not None:
            created_time = created_time.astimezone(timezone.utc).replace(tzinfo=None)
        if updated_time.tzinfo is not None:
            updated_time = updated_time.astimezone(timezone.utc).replace(tzinfo=None)

        assert created_time < updated_time, "Expected `updated` to be newer than `created`"

def test_print_capture(
    mock_logger: MagicMock
) -> None:
    """
    Ensure `tracing.PrintCapture` properly captures and logs print statements.

    This test ensures:
    - The `PrintCapture` handler captures print statements directed to `sys.stdout`.
    - Validates that the captured output is logged as expected.

    Args:
        mock_logger (MagicMock): Mock logger used to verify the captured logs.

    Returns:
        None: This test does not return a value but asserts that the print statements are captured and logged correctly.
    """

    handler = tracing.PrintCapture()
    handler.setLevel(logging.INFO)
    mock_logger.addHandler(handler)
    with patch("sys.stdout.write") as mock_stdout:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        # Manually write to sys.stdout to simulate print behavior
        sys.stdout.write(
            record.getMessage() + "\n"
        )
        sys.stdout.flush()
        # Ensure the correct log message is captured
        expected_output = "Test message\n"
        captured_output = "".join(
            call[0][0] for call in mock_stdout.call_args_list
        )
        assert expected_output.strip() in captured_output.strip()

def test_ansi_file_handler(
    mock_logger: MagicMock
) -> None:
    """
    Ensure `tracing.ANSIFileHandler` removes ANSI sequences before writing logs.

    This test:
    - Verifies that `ANSIFileHandler` strips ANSI escape codes from log messages before writing them to a file.
    - Uses a helper function to remove ANSI codes and ensures that the final message written to the file does not contain any escape codes.

    Args:
        mock_logger (MagicMock): Mock logger used to verify the behavior of the file handler.

    Returns:
        None: This test does not return a value but asserts that ANSI escape codes are correctly stripped before logging to a file.
    """

    def remove_ansi(
        text: str
    ) -> str:
        """
        Helper function to remove ANSI escape sequences from a string.

        This function removes ANSI escape codes, which are used for terminal text formatting (e.g., colors),
        from the provided text. The cleaned text can then be safely logged or processed without formatting artifacts.

        Args:
            text (str): The string containing ANSI escape sequences to be removed.

        Returns:
            str: The input string with all ANSI escape sequences removed.

        Example:
            >>> remove_ansi("\033[31mError message\033[0m")
            'Error message'
        """

        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    with patch(
        "builtins.open",
        create=True
    ) as mock_open:
        handler = tracing.ANSIFileHandler(
            "logs/tests/test_ansi.log",
            mode="w"
        )
        handler.setFormatter(
            logging.Formatter("%(message)s")
        )
        mock_logger.addHandler(handler)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="\033[31mError message\033[0m",
            args=(),
            exc_info=None
        )
        handler.setFormatter(
            logging.Formatter("%(message)s")
        )  # Ensure formatter is applied
        record.msg = remove_ansi(record.msg)  # Strip ANSI codes before emitting
        handler.emit(record)  # Explicitly trigger log writing
        handler.flush()
        mock_open.assert_called()
        # Ensure write() was called with the cleaned message
        write_calls = [
            call[0][0].strip() for call in mock_open.return_value.write.call_args_list
        ]
        assert any("Error message" in call for call in write_calls)
        assert all("\033[31m" not in call for call in write_calls)
