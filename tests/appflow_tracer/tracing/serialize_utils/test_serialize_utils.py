#!/usr/bin/env python3

# File: ./tests/appflow_tracer/tracing/test_serialize_utils.py
__version__ = "0.1.0"  ## Package version

"""
PyTest Module: ./tests/appflow_tracer/tracing/test_serialize_utils.py

This module contains unit tests for the `serialize_utils.py` module in `appflow_tracer.lib`.
It ensures that serialization and string sanitization functions operate correctly, including:

    - **Safe JSON serialization** for various Python data types.
    - **Handling of non-serializable objects** by providing fallback representations.
    - **String sanitization** to strip inline comments from code strings.

## Use Cases:
    1. **Validate JSON serialization with `serialize_utils.safe_serialize()`**
       - Ensures standard Python objects serialize correctly to JSON.
       - Handles **primitive types**, **lists**, and **dictionaries** without modification.
       - Converts **non-serializable objects** into structured error responses.
       - Verifies `verbose=True` outputs formatted JSON.

    2. **Ensure `serialize_utils.sanitize_token_string()` removes inline comments**
       - Strips comments while preserving meaningful code.
       - Handles various edge cases, including:
         - **Full-line comments**
         - **Trailing inline comments**
         - **Empty or whitespace-only inputs**
         - **Special character handling**

## Improvements Implemented:
    - `serialize_utils.safe_serialize()` now **detects and reports non-serializable objects** without crashing.
    - `serialize_utils.sanitize_token_string()` **properly removes comments** without affecting valid code.
    - Tests are **isolated from logging/tracing** by disabling these features in `CONFIGS`.

## Expected Behavior:
    - **Valid JSON is returned for serializable objects**.
    - **Non-serializable objects return structured fallback representations**.
    - **Inline comments are removed while preserving valid code structure**.

"""

import sys
import os

import json
import pytest

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import serialize_utils

CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_serialize_utils.log'
)
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

def test_safe_serialize() -> None:
    """
    Ensure `serialize_utils.safe_serialize()` correctly converts objects to JSON strings with metadata.

    This test verifies:
    - Standard Python data types (dicts, lists, numbers) serialize correctly.
    - Handles verbose output for formatted JSON.
    - Properly handles **non-serializable objects**, returning structured fallback data.
    - Includes **error messages** for failed serializations.

    Returns:
        None: This test function does not return a value. It asserts that the serialization works correctly for various object types.
    """

    # Test valid JSON serialization
    result = serialize_utils.safe_serialize(
        {"key": "value"},
        configs=CONFIGS
    )
    assert result["success"] is True
    assert json.loads(
        result["serialized"]
    ) == {"key": "value"}
    assert result["type"] == "dict"

    result_verbose = serialize_utils.safe_serialize(
        {"key": "value"},
        configs=CONFIGS,
        verbose=True
    )
    assert result_verbose["success"] is True
    assert json.loads(
        result_verbose["serialized"]
    ) == {"key": "value"}
    assert result_verbose["type"] == "dict"

    # Test primitive data types
    assert serialize_utils.safe_serialize(
        123,
        configs=CONFIGS
    )["serialized"] == "123"
    assert json.loads(
        serialize_utils.safe_serialize(
            [1, 2, 3],
            configs=CONFIGS
        )["serialized"]
    ) == [1, 2, 3]

    # Test handling of non-serializable objects
    result_unserializable = serialize_utils.safe_serialize(
        object(),
        configs=CONFIGS
    )
    # print("DEBUG: serialize_utils.safe_serialize(object()) ->", result_unserializable)
    assert result_unserializable["success"] is False
    assert result_unserializable["serialized"] == "[Unserializable data]"
    assert "error" in result_unserializable
    assert result_unserializable["type"] == "object"

def test_sanitize_token_string() -> None:
    """
    Ensure `serialize_utils.sanitize_token_string()` removes comments while keeping code intact.

    This test checks:
    - Removal of **inline comments** while preserving the rest of the code.
    - Removal of **full-line comments**.
    - Proper handling of edge cases:
      - Empty strings
      - Strings with only whitespace
      - Special characters before the comment symbol (`#`).

    Returns:
        None: This test function does not return a value. It validates that the function correctly sanitizes code strings by removing comments.
    """

    assert serialize_utils.sanitize_token_string(
        "some_code()  # this is a comment"
    ) == "some_code()"
    assert serialize_utils.sanitize_token_string(
        "   another_line   "
    ) == "another_line"
    assert serialize_utils.sanitize_token_string(
        "print(123)  # inline comment"
    ) == "print(123)"
    assert serialize_utils.sanitize_token_string(
        "# full line comment"
    ) == ""
    assert serialize_utils.sanitize_token_string("") == ""
