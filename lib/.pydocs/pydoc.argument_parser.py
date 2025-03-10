#!/usr/bin/env python3

# Python File: ./lib/argument_parser.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
Overview
    The `argument_parser.py` module provides command-line argument parsing for system configurations.
    It supports structured argument definitions from JSON configuration files.

Core Features:
    - Loads argument configurations from system parameter files.
    - Parses command-line arguments based on predefined options.
    - Supports type conversion and validation for arguments.
    - Enables debug mode for detailed argument inspection.

Expected Behavior & Usage:
    Parsing CLI Arguments:
        from lib.argument_parser import parse_arguments
        args = parse_arguments(context=["debug", "verbose"], description="Azure CLI utility")
        print(args.debug, args.verbose)
"""

FUNCTION_DOCSTRINGS = {
    "load_argument_config": """
    Loads argument definitions from a predefined JSON configuration file.

    Returns:
        Dict[str, Any]: Parsed argument definitions categorized by section.
""",
    "convert_types": """
    Converts type annotations in argument definitions from string format to Python types.

    Parameters:
        kwargs (Dict[str, Any]): Argument definition containing type annotations.

    Returns:
        Dict[str, Any]: The argument definition with correct type mappings.
""",
    "parse_arguments__prototype": """
    Parses command-line arguments based on predefined configurations.

    Parameters:
        context (Dict[str, Any], optional): Limits parsed arguments to the specified context. Defaults to None.
        description (str, optional): Custom description for the argument parser. Defaults to "Azure CLI utility".

    Returns:
        argparse.Namespace: Parsed command-line arguments.
""",
    "parse_arguments": """
    Parses command-line arguments using a structured parameter definition.

    Parameters:
        args (Dict[str, Any]): System parameter configurations defining available arguments.

    Returns:
        argparse.Namespace: The parsed arguments as an object.
""",
    "main": """
    Main function to execute argument parsing and display parsed results.
"""
}

VARIABLE_DOCSTRINGS = {
    "system_params_filepath": "Path to the JSON file containing system argument definitions."
}
