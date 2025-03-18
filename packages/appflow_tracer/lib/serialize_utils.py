#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/serialize_utils.py

__package__ = "packages.appflow_tracer.lib"
__module__ = "serialize_utils"

__version__ = "0.1.0"  ## Package version

#-------------------------------------------------------------------------------

# Standard library imports - Core system module
import sys

# Standard library imports - Utility modules
import json  # Handles JSON serialization and deserialization
import tokenize  # Used for tokenizing Python source code

# Standard library imports - IO operations
from io import StringIO  # In-memory file-like object

# Standard library imports - File system-related module
from pathlib import Path

#-------------------------------------------------------------------------------

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

#-------------------------------------------------------------------------------

# Import category from system_variables
from lib.system_variables import (
    default_indent,
    category
)
from . import log_utils

#-------------------------------------------------------------------------------

def safe_serialize(
    data: any,
    configs: dict,
    verbose: bool = False
) -> dict:

    try:
        json_dumps = json.dumps(
            data,
            indent=default_indent if verbose else None,
            default=str,
            ensure_ascii=False
        )
        # Ensure that complex objects aren't falsely marked as serializable
        if isinstance(data, object) and not isinstance(data, (dict, list, tuple, str, int, float, bool, set, type(None))):
            raise TypeError("Object is not JSON serializable")
        serialized_data = {"success": True, "serialized": json_dumps, "type": type(data).__name__}
        # log_utils.log_message(
        #     f'\nSerialized Data: {serialized_data}',
        #     log_category=category.debug.id,
        #     configs=configs
        # )
        return serialized_data
    except (TypeError, ValueError) as e:
        # Handle objects with attributes (custom classes)
        if hasattr(data, "__dict__"):
            serialized_attrs = {k: str(v) for k, v in vars(data).items()}
            serialized_data = {
                "success": False,
                "serialized": json.dumps(
                    serialized_attrs,
                    indent=default_indent if verbose else None,
                    ensure_ascii=False
                ),
                "type": type(data).__name__,
                "error": str(e)
            }
        # Handle iterators (list, tuple, set)
        elif hasattr(data, "__iter__") and not isinstance(data, (str, bytes, dict)):
            try:
                serialized_data = {
                    "success": False,
                    "serialized": json.dumps(
                        list(data),
                        indent=default_indent if verbose else None,
                        ensure_ascii=False
                    ),
                    "type": "iterator",
                    "error": "Converted from iterator"
                }
            except Exception as iter_error:
                serialized_data = {
                    "success": False,
                    "serialized": "[Unserializable iterator]",
                    "type": "iterator",
                    "error": str(iter_error)
                }
        # Default fallback for completely non-serializable objects
        else:
            serialized_data = {
                "success": False,
                "serialized": "[Unserializable data]",
                "type": type(data).__name__,
                "error": str(e)
            }
        # log_utils.log_message(
        #     f'\nSerialized Data: {serialized_data}',
        #     log_category=category.debug.id,
        #     configs=configs
        # )
        return serialized_data

#-------------------------------------------------------------------------------

def sanitize_token_string(
    line: str
) -> str:

    # # Legacy code:
    # try:
    #     tokens = tokenize.generate_tokens(StringIO(line).readline)
    #     new_line = []
    #     last_token_was_name = False  # Track if the last token was an identifier or keyword
    #     for token in tokens:
    #         if token.type == tokenize.COMMENT:
    #             break  # Stop at the first comment outside of strings
    #         if last_token_was_name and token.type in (tokenize.NAME, tokenize.NUMBER):
    #             new_line.append(" ")  # Add space between concatenated names/numbers
    #         new_line.append(token.string)
    #         last_token_was_name = token.type in (tokenize.NAME, tokenize.NUMBER)
    #         new_line = "".join(new_line).strip()  # Trim spaces/tabs/newlines
    #     return new_line
    #     # return "".join(new_line).strip()  # Trim spaces/tabs/newlines
    # except Exception:
    #     return line.strip()  # Ensure fallback trims spaces

    try:
        tokens = tokenize.generate_tokens(StringIO(line).readline)
        new_line = []
        last_token_was_name = False  # Track if the last token was an identifier or keyword

        for token in tokens:
            if token.type == tokenize.COMMENT:
                break  # Stop at the first comment outside of strings
            if last_token_was_name and token.type in (tokenize.NAME, tokenize.NUMBER):
                new_line.append(" ")  # Add space between concatenated names/numbers
            new_line.append(token.string)
            last_token_was_name = token.type in (tokenize.NAME, tokenize.NUMBER)

        return "".join(new_line).strip()  # Trim spaces/tabs/newlines
    except Exception:
        return line.strip()  # Ensure fallback trims spaces

#-------------------------------------------------------------------------------

def main() -> None:
    pass

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
