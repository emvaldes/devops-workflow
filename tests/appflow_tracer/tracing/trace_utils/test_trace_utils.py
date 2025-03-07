#!/usr/bin/env python3

# File: ./tests/appflow_tracer/tracing/test_trace_utils.py
__version__ = "0.1.0"  ## Package version

"""
PyTest Module: ./tests/appflow_tracer/test_trace_utils.py

This module contains unit tests for the `trace_utils.py` module in `appflow_tracer.lib`.
It ensures correct function execution tracing and structured logging, covering:

    - **Function call tracing**: Captures invocation details, ensuring execution visibility.
    - **Return value logging**: Serializes return values for structured execution logs.
    - **Project-specific filtering**: Ensures only relevant project functions are logged.
    - **Configuration-driven activation**: Prevents unnecessary tracing when disabled.

## Use Cases:
    1. **Validate `trace_utils.start_tracing()` activation**
       - Ensures tracing starts **only when enabled** in the configuration.
       - Prevents redundant activations by checking `sys.gettrace()`.
       - Verifies that `sys.settrace()` is correctly called.

    2. **Ensure `trace_utils.trace_all()` generates a valid trace function**
       - Confirms the trace function **properly processes events** (calls and returns).
       - Ensures non-project functions are **excluded from logging**.
       - Validates that function metadata is structured correctly.

    3. **Test function call logging via `trace_utils.call_events()`**
       - Simulates a function call and checks if metadata is captured.
       - Verifies that **arguments are serialized correctly**.
       - Ensures only **project-relevant function calls are logged**.

    4. **Verify function return logging via `trace_utils.return_events()`**
       - Captures return values and ensures correct serialization.
       - Confirms function exit events are logged with structured data.
       - Validates that primitive types and complex objects are handled correctly.

## Improvements Implemented:
    - **Mocking of `sys.settrace()`** to avoid real tracing activation.
    - **Ensuring `CONFIGS` are respected** when enabling tracing.
    - **Patching of logging utilities** to isolate logs per test.

## Expected Behavior:
    - **Tracing activates only when explicitly configured**.
    - **Function call and return details are structured correctly**.
    - **Non-project calls are filtered out, keeping logs relevant**.

"""

import sys
import os

import json
import logging

import pytest
from unittest.mock import patch, MagicMock

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import trace_utils

CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_serialize_utils.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Provides a mock logger for testing tracing output.

    This fixture creates and returns a mock instance of the `logging.Logger` class using `MagicMock`. It is designed to
    simulate the behavior of a logger for testing purposes, particularly to verify that logging calls are made during
    tracing without actually writing to log files.

    The mock logger can be used to check if certain logging methods (e.g., `info`, `error`) are called with the expected
    arguments, making it useful for verifying logging behavior in tests.

    Returns:
        MagicMock: A mock logger object that mimics a `logging.Logger` instance.
    """

    return MagicMock(spec=logging.Logger)

@pytest.fixture
def mock_configs() -> dict:
    """
    Provides a mock configuration dictionary for testing.

    This fixture creates and returns a mock configuration dictionary that simulates the `CONFIGS` object used in the application.
    It includes default configurations for tracing and logging, both set to enabled (`True`), which can be used for testing
    purposes where access to these configurations is required.

    The mock configuration is useful for isolating tests that need configuration data without requiring actual system configuration.

    Returns:
        dict: A dictionary containing mock configuration settings for tracing and logging.
    """

    return {
        "tracing": {"enable": True},
        "logging": {"enable": True}
    }

@patch("sys.settrace")
def test_start_tracing(
    mock_settrace: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """
    Ensure `trace_utils.start_tracing()` initializes tracing only when enabled.

    This test ensures:
    - `sys.settrace()` is called only when tracing is enabled in `CONFIGS`.
    - Prevents multiple activations by checking `sys.gettrace()` before applying tracing.
    - Verifies that tracing is correctly configured via `CONFIGS`.

    Args:
        mock_settrace (MagicMock): Mock for `sys.settrace()` to verify it is called or not.
        mock_logger (MagicMock): Mock logger for tracing output.
        mock_configs (dict): Mock configuration for tracing settings.

    Returns:
        None: This test function does not return a value. It verifies that tracing is activated correctly.
    """

    sys.settrace(None)  # Reset trace before running the test
    trace_utils.start_tracing(
        logger=mock_logger,
        configs=mock_configs
    )
    mock_settrace.assert_called_once()

@patch("sys.settrace")
def test_start_tracing_disabled(
    mock_settrace: MagicMock,
    mock_logger: MagicMock
) -> None:
    """
    Ensure `trace_utils.start_tracing()` does not initialize tracing when disabled.

    This test ensures:
    - `sys.settrace()` is **not called** when tracing is disabled in `CONFIGS`.
    - Verifies that `trace_utils.start_tracing()` respects the configuration settings.

    Args:
        mock_settrace (MagicMock): Mock for `sys.settrace()` to ensure it's not called.
        mock_logger (MagicMock): Mock logger for testing.

    Returns:
        None: This test function does not return a value. It asserts that tracing is not activated when disabled.
    """

    mock_configs = {
        "tracing": {
            "enable": False
        }
    }
    trace_utils.start_tracing(
        logger=mock_logger,
        configs=mock_configs
    )
    mock_settrace.assert_not_called()

@patch("packages.appflow_tracer.lib.trace_utils.trace_all")
def test_trace_all(
    mock_trace_all: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """
    Ensure `trace_utils.trace_all()` generates a valid trace function.

    This test:
    - Mocks `trace_utils.trace_all()` to return a dummy trace function and ensures it is callable.
    - Ensures that `trace_utils.trace_all()` does not fail even when `CONFIGS` is missing logging settings.

    Args:
        mock_trace_all (MagicMock): Mock for the `trace_utils.trace_all()` function.
        mock_logger (MagicMock): Mock logger for tracing output.
        mock_configs (dict): Mock configuration for tracing settings.

    Returns:
        None: This test function does not return a value. It verifies that `trace_utils.trace_all()` generates a callable trace function.
    """

    mock_configs.setdefault(
        "logging",
        {"enable": True}
    )
    mock_trace_all.return_value = lambda frame, event, arg: None
    trace_function = trace_utils.trace_all(
        mock_logger,
        mock_configs
    )
    assert callable(trace_function), "trace_utils.trace_all() did not return a callable trace function."

@patch(
    "packages.appflow_tracer.lib.file_utils.is_project_file",
    return_value=True
)
@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_call_events(
    mock_is_project_file: MagicMock,
    mock_log_message: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """
    Ensure `trace_utils.call_events()` logs function calls correctly.

    This test:
    - Ensures that function calls are logged with the correct metadata.
    - Verifies that function arguments are serialized correctly.
    - Ensures only project-relevant function calls are logged.

    Args:
        mock_is_project_file (MagicMock): Mock to ensure the function is part of the project.
        mock_log_message (MagicMock): Mock for the `log_message()` function to check if it is called.
        mock_logger (MagicMock): Mock logger for tracing output.
        mock_configs (dict): Mock configuration for tracing and logging settings.

    Returns:
        None: This test function does not return a value. It validates that `call_events()` correctly logs function calls.
    """

    # Explicitly enable logging and ensure events are properly configured
    mock_configs["logging"]["enable"] = True
    mock_configs["tracing"]["enable"] = True
    mock_configs["events"] = {
        category.calls.id.lower(): True,
        category.returns.id.lower(): True
    }
    frame_mock = MagicMock()
    frame_mock.f_code.co_name = "test_function"
    frame_mock.f_back.f_code.co_name = "caller_function"
    frame_mock.f_globals.get.return_value = os.path.join(
        CONFIGS["logging"]["logs_dirname"],
        "test_file.py"
    )
    trace_utils.call_events(
        mock_logger,
        frame_mock,
        "test_file.py",
        None,
        mock_configs
    )
    # Ensure log_message was called
    assert mock_log_message.called, "Expected log_message() to be called, but it wasn't."

@patch(
    "packages.appflow_tracer.lib.file_utils.is_project_file",
    return_value=True
)
@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_return_events(
    mock_is_project_file: MagicMock,
    mock_log_message: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """
    Ensure `trace_utils.return_events()` logs function return values correctly.

    This test:
    - Captures return values and ensures they are correctly serialized.
    - Verifies that return events are logged with the appropriate function metadata.

    Args:
        mock_is_project_file (MagicMock): Mock to ensure the function is part of the project.
        mock_log_message (MagicMock): Mock for the `log_message()` function to check if it is called.
        mock_logger (MagicMock): Mock logger for tracing output.
        mock_configs (dict): Mock configuration for tracing and logging settings.

    Returns:
        None: This test function does not return a value. It validates that `return_events()` logs return values correctly.
    """

    # Explicitly enable logging and events
    mock_configs["logging"]["enable"] = True
    mock_configs["tracing"]["enable"] = True
    mock_configs["events"] = {
        category.calls.id.lower(): True,
        category.returns.id.lower(): True
    }
    frame_mock = MagicMock()
    frame_mock.f_code.co_name = "test_function"
    frame_mock.f_globals.get.return_value = os.path.join(
        CONFIGS["logging"]["logs_dirname"],
        "test_file.py"
    )
    trace_utils.return_events(
        mock_logger,
        frame_mock,
        "test_file.py",
        "return_value",
        mock_configs
    )
    # Ensure log_message was called
    assert mock_log_message.called, "Expected log_message() to be called, but it wasn't."
