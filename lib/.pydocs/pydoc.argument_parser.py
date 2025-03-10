#!/usr/bin/env python3

# Python File: ./lib/argument_parser.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./lib/argument_parser.py

Description:
    The argument_parser.py module provides structured argument parsing capabilities for CLI-based Python applications.
    It dynamically loads argument configurations from a system-defined JSON file and ensures type conversions, validation, and error handling.
    This module simplifies command-line argument management while maintaining flexibility for different contexts.

Core Features:
    - Argument Configuration Loading: Reads argument structures from an external JSON configuration file.
    - Dynamic Argument Parsing: Uses argparse to define CLI arguments dynamically based on pre-configured rules.
    - Type Conversion: Automatically converts CLI arguments to expected data types.
    - Debugging & Validation: Provides debugging output for parsed arguments and handles incorrect JSON structures gracefully.
    - CLI Integration: Supports manual and pre-configured argument handling.

Usage:
    Basic Argument Parsing:
        from lib.argument_parser import parse_arguments
        args = parse_arguments(context={"debug", "verbose"})

    Loading External Configurations:
        from lib.argument_parser import load_argument_config
        config = load_argument_config()

Dependencies:
    - sys - Used for argument handling and error output.
    - os - Provides system-related utilities.
    - json - Parses JSON-based argument configuration.
    - logging - Logs debugging information and errors.
    - argparse - Handles CLI argument parsing.
    - pathlib - Resolves system file paths dynamically.
    - typing (Dict, Any) - Defines type hints for functions.

Global Variables:
    - system_params_filepath: The file path for the system-defined argument configuration file.

CLI Integration:
    This script can be executed via CLI to test argument parsing.

Example Execution:
    python argument_parser.py --debug

Expected Behavior:
    - Successfully loads and parses CLI arguments.
    - Converts arguments to expected types.
    - Handles missing or invalid arguments gracefully.
    - Provides debugging output when enabled.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Error encountered during argument parsing.
"""

FUNCTION_DOCSTRINGS = {
    "load_argument_config": """
    Function: load_argument_config() -> Dict[str, Any]
    Description:
        Loads CLI argument configurations from a JSON file. Ensures the file exists and contains a valid JSON structure.

    Returns:
        - Dict[str, Any]: Parsed JSON dictionary containing argument configurations.

    Behavior:
        - Checks if the argument configuration file exists.
        - Reads the file contents and attempts to parse JSON data.
        - Ensures the file is not empty and contains a valid JSON structure.

    Error Handling:
        - Raises FileNotFoundError if the configuration file is missing.
        - Raises ValueError if the JSON structure is invalid or empty.
        - Raises RuntimeError if any other error occurs while reading the file.
    """,
    "convert_types": """
    Function: convert_types(kwargs: Dict[str, Any]) -> Dict[str, Any]
    Description:
        Converts string-based type definitions into callable Python types.

    Parameters:
        - kwargs (Dict[str, Any]): Dictionary containing argument properties.

    Returns:
        - Dict[str, Any]: Updated dictionary with correct type mappings.

    Behavior:
        - If 'store_true' is used as an action, removes the 'type' property to prevent conflicts.
        - Converts 'type' values from string format (e.g., 'str', 'int', 'bool') to actual Python types.
    """,
    "parse_arguments__prototype": """
    Function: parse_arguments__prototype(context: Dict[str, Any] = None, description: str = "Azure CLI utility") -> argparse.Namespace
    Description:
        Parses command-line arguments using pre-configured settings, allowing context-based filtering.

    Parameters:
        - context (Dict[str, Any], optional): Defines which arguments should be considered. Defaults to None.
        - description (str, optional): Description displayed in the CLI help text. Defaults to "Azure CLI utility".

    Returns:
        - argparse.Namespace: Parsed CLI arguments stored in a namespace.

    Behavior:
        - Loads argument configurations from load_argument_config().
        - Iterates through sections and parameters, dynamically adding them to the argparse parser.
        - Uses convert_types() to ensure argument types are properly handled.
        - If debugging is enabled, prints parsed arguments in JSON format.

    Error Handling:
        - Captures and reports errors related to missing or malformed argument configurations.
    """,
    "parse_arguments": """
    Function: parse_arguments(args: Dict[str, Any]) -> argparse.Namespace
    Description:
        Parses command-line arguments from a structured dictionary format.

    Parameters:
        - args (Dict[str, Any]): Dictionary containing argument structures, including options and flags.

    Returns:
        - argparse.Namespace: Parsed CLI arguments stored in a namespace.

    Behavior:
        - Iterates through argument sections and processes options dynamically.
        - Ensures type conversion for numerical and boolean values.
        - Logs and reports unknown or missing argument definitions.
        - Uses argparse to add dynamically defined arguments.

    Error Handling:
        - Captures missing 'flags' definitions and logs an error.
        - Catches failures in argument parsing and logs a critical error.
    """,
    "main": """
    Function: main() -> None
    Description:
        Main execution function that initializes argument parsing.

    Behavior:
        - Calls parse_arguments() to retrieve argument values.
        - Prints parsed argument values for debugging.
    """,
}

VARIABLE_DOCSTRINGS = {
    "system_params_filepath": """
    - Description: Defines the file path for the argument configuration JSON file.
    - Type: Path
    - Usage: Used by load_argument_config() to load CLI argument settings.
    """
}
