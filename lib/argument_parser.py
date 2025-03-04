#!/usr/bin/env python3

# File: ./lib/argument_parser.py
# Version: 0.1.0

"""
File: ./lib/argument_parser.py

Description:
    Command-Line Argument Parser
    This module provides dynamic parsing of command-line arguments based on a JSON configuration file.
    It supports structured parameter definitions, automatic type conversion, and flexible flag handling.

Core Features:
    - **JSON-Based Argument Loading**: Reads structured argument definitions dynamically.
    - **Automatic Type Conversion**: Converts CLI argument values to expected Python types.
    - **Structured Validation**: Ensures required and optional arguments are handled correctly.
    - **Debugging Support**: Displays parsed arguments in JSON format when `--debug` is used.

Usage:
    To run argument parsing with debug output:
    ```bash
    python argument_parser.py --debug
    ```

Dependencies:
    - argparse
    - json
    - logging
    - system_variables (for directory paths and settings)

Global Variables:
    - `system_params_filepath` (Path): Stores the path to the JSON configuration file.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to errors in argument parsing or configuration loading.

Example:
    ```bash
    python argument_parser.py --debug
    ```
"""

# Package version
__version__ = "0.1.0"

import sys
import os

import json
import logging
import argparse

from typing import Dict, Any
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from system_variables import (
    system_params_filepath
)

def load_argument_config() -> Dict[str, Any]:
    """
    Load argument definitions from a JSON configuration file and validate them.

    Reads a structured JSON file that defines command-line arguments, ensuring the file exists,
    is correctly formatted, and contains valid content.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed argument definitions.

    Raises:
        FileNotFoundError: If the JSON configuration file does not exist.
        ValueError: If the JSON file is empty or contains invalid JSON.
        RuntimeError: If an unexpected error occurs while reading the file.

    Notes:
        - If the JSON configuration file is missing, execution is halted with an error.
        - JSON parsing errors are logged to prevent execution failures.
    """

    if not system_params_filepath.exists():
        raise FileNotFoundError(f'ERROR: Argument configuration file not found at {system_params_filepath}')
    ## Handles empty files, permission issues, and invalid JSON.
    try:
        with open(system_params_filepath, "r") as file:
            data = json.load(file)
            if not data:
                raise ValueError(f'ERROR: Empty JSON file "{system_params_filepath}". Please check the contents.')
            return data
    except json.JSONDecodeError as e:
        raise ValueError(
            f'ERROR: Invalid JSON structure in "{system_params_filepath}".\nDetails: {e}'
        )
    except Exception as e:
        raise RuntimeError(f'ERROR: Unable to read "{system_params_filepath}". Details: {e}')

def convert_types(
    kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert JSON type definitions into actual Python types.

    This function modifies the argument properties dictionary by converting
    type definitions from string format (e.g., "str", "int") into their corresponding
    Python types.

    Args:
        kwargs (Dict[str, Any]): Dictionary of argument properties, potentially including a `type` field.

    Returns:
        Dict[str, Any]: Updated dictionary with the `type` field converted to a Python type if applicable.

    Notes:
        - If `action="store_true"` is set, the `type` field is removed to avoid conflicts.
        - Supports automatic conversion of `str`, `int`, and `bool` type definitions.
    """

    type_mapping = {"str": str, "int": int, "bool": bool}
    ## Remove "type" if "store_true" action is set
    if "action" in kwargs and kwargs["action"] == "store_true":
        kwargs.pop("type", None)  ## Safely remove "type" if it exists
    elif "type" in kwargs and kwargs["type"] in type_mapping:
        kwargs["type"] = type_mapping[kwargs["type"]]
    return kwargs

def parse_arguments__prototype(
    context: Dict[str, Any] = None,
    description: str = "Azure CLI utility"
) -> argparse.Namespace:
    """
    Parse command-line arguments dynamically based on a JSON configuration file.

    This function loads structured argument definitions from a JSON file and dynamically
    adds them to an argparse parser. It supports automatic type conversion and structured validation.

    Args:
        context (Dict[str, Any], optional): A dictionary specifying which arguments should be included. Defaults to None.
        description (str, optional): A description for the command-line utility. Defaults to "Azure CLI utility".

    Returns:
        argparse.Namespace: A namespace containing the parsed arguments as attributes.

    Raises:
        Exception: If an error occurs while processing arguments.

    Workflow:
        1. Loads argument definitions from a JSON file.
        2. Iterates through the defined sections and adds them to the argparse parser.
        3. Converts argument types as needed and applies appropriate argument flags.
        4. Parses command-line arguments and returns them in a structured namespace.

    Notes:
        - Required arguments are manually enforced in `main()`, rather than in `argparse`.
        - If `--debug` is provided, the parsed arguments are printed in JSON format.
    """

    parser = argparse.ArgumentParser(description=description)
    argument_definitions = load_argument_config()
    for section_name, parameters in argument_definitions.items():
        for arg_name, arg_data in parameters.items():
            if context and arg_name not in context:
                continue
            flags = arg_data.get("flags", [])
            kwargs = convert_types(arg_data.get("kwargs", {}))
            ## Override 'required' for manual enforcement in `main()`
            if "required" in kwargs:
                kwargs.pop("required")
            parser.add_argument(*flags, **kwargs)
    args = parser.parse_args()
    ## Improves readability of CLI arguments.
    ## Debug mode: Show parsed arguments
    if getattr(args, "debug", False):
        print("\nParsed CLI Arguments (JSON):")
        ## for key, value in vars(args).items():
        ##     print(f'{key}: {value}')
        print(json.dumps(vars(args), indent=4))
    return args

def parse_arguments(
    args: Dict[str, Any]
) -> argparse.Namespace:
    """
    Process structured CLI arguments using argparse.

    This function manually processes each argument defined in a structured dictionary,
    ensuring correct type conversions and handling unknown arguments gracefully.

    Args:
        args (Dict[str, Any]): A dictionary containing structured argument definitions.

    Returns:
        argparse.Namespace: A namespace containing the parsed arguments as attributes.

    Raises:
        Exception: If an error occurs while adding arguments.

    Workflow:
        1. Reads structured arguments from `args` dictionary.
        2. Converts type definitions from strings (e.g., `"int"`) to Python types.
        3. Iterates over argument sections and adds them to an `argparse` parser.
        4. Parses arguments and stores them in a namespace.
        5. Logs any unknown arguments encountered.

    Notes:
        - If `store_true` or `store_false` actions are used, the `type` field is removed to prevent conflicts.
        - If an argument is missing its `flags` field, an error is logged.
    """

    parser = argparse.ArgumentParser(description="System Globals Parameter Parser")
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool
    }

    # print(f'System Parameters (loaded): {json.dumps(args, indent=4)}')

    parsed_args = {}  # Store parsed arguments manually
    for section, section_data in args.items():
        if "options" in section_data:
            for param, details in section_data["options"].items():
                print()
                logging.debug(f'Processing: {section}["{param}"]')
                print(json.dumps(details, indent=4))
                # Ensure type conversion
                kwargs = details.get("kwargs", {}).copy()
                # Remove `required=True` to allow missing values to be handled manually
                kwargs.pop("required", None)
                # If action is store_true or store_false, remove type to avoid conflict
                if "action" in kwargs and kwargs["action"] in ["store_true", "store_false"]:
                    kwargs.pop("type", None)
                # Convert type from string to callable
                if "type" in kwargs and isinstance(kwargs["type"], str):
                    kwargs["type"] = type_mapping.get(kwargs["type"], str)
                # Check if flags exist before calling parser.add_argument
                flags = details.get("flags")
                if not flags:
                    logging.error(f'Missing "flags" in argument: {param}')
                    continue
                try:
                    parser.add_argument(*flags, **kwargs)
                except Exception as e:
                    logging.error(f'Failed to add argument {param} in section {section} with details {kwargs}: {e}')
                    raise
    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    # Log any unknown arguments that were ignored
    if unknown:
        logging.warning(f'Unknown CLI arguments ignored: {unknown}')

    return args

def main() -> None:
    """
    Main function for executing argument parsing when the script is run as a standalone module.

    This function loads the argument configuration, parses command-line arguments, and
    prints the parsed values in a structured JSON format.

    Returns:
        None: This function does not return values; it prints parsed argument data.

    Raises:
        Exception: If argument parsing fails.

    Workflow:
        1. Calls `parse_arguments()` to process command-line arguments.
        2. Displays parsed argument values in a structured JSON format.
        3. Logs errors if any required arguments are missing.

    Notes:
        - If the `--debug` flag is present, the parsed arguments are printed in JSON format.
        - Ensures that command-line arguments are validated and processed correctly.
    """

    args = parse_arguments()
    print("\nArgument parsing completed successfully.")
    print(json.dumps(vars(args), indent=4))

if __name__ == "__main__":
    main()
