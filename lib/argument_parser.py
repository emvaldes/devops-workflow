#!/usr/bin/env python3

# File: ./lib/argument_parser.py
__version__ = "0.1.0"  ## Package version

import sys
import os

import json
import logging
import argparse

from typing import Dict, Any

from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.system_variables import (
    system_params_filepath
)

def load_argument_config() -> Dict[str, Any]:

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

    args = parse_arguments()
    print("\nArgument parsing completed successfully.")
    print(json.dumps(vars(args), indent=4))

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
