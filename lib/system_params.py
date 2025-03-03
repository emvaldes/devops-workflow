#!/usr/bin/env python3

"""
File: ./lib/system_params.py

Description:
    System Parameter Management
    This module handles system-wide parameter management by loading runtime
    parameters from JSON configuration files and merging them with environment variables.

Core Features:
    - **Configuration Loading**: Reads parameters from `runtime-params.json`, `project-params.json`, and `default-params.json`.
    - **Environment Variable Management**: Dynamically sets system-wide environment variables.
    - **Validation and Error Handling**: Ensures required parameters are initialized before execution.

Usage:
    To load and initialize system parameters:
    ```bash
    python system_params.py
    ```

Dependencies:
    - os
    - json
    - logging
    - dotenv
    - pathlib
    - lib.configure_params (for JSON merging and validation)

Global Variables:
    - `SYSTEM_PARAMS` (dict): Loaded system-wide parameters.
    - `RUNTIME_PARAMS` (dict): Parameters dynamically merged at runtime.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to missing configuration files or invalid environment variables.

Example:
    ```bash
    python system_params.py
    ```
"""

import sys
import os

import json
import logging

from dotenv import load_dotenv
from typing import Optional  # Import Optional for type hints

from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.configure_params import main as configure_params
from lib.configure_params import load_json_sources

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

from system_variables import (
    project_root,
    runtime_params_filename,
    runtime_params_filepath,
    system_params_filepath,
    system_params_listing,
    project_params_filepath,
    default_params_filepath
)

def load_json_config(
    runtime_params_filepath: Path
) -> dict:
    """
    Load environment variables from a JSON configuration file.

    Reads a JSON file and ensures its structure is valid before returning
    the parsed contents.

    Args:
        runtime_params_filepath (Path): The file path of the JSON configuration file.

    Raises:
        ValueError: If the JSON file is empty or has an invalid structure.
        RuntimeError: If the file cannot be read.

    Returns:
        dict: The parsed JSON data containing system parameters.

    Notes:
        - If the file is empty, the function raises a `ValueError`.
        - If the file contains invalid JSON, the function raises `RuntimeError`.
        - Ensures robust error handling for corrupt or missing files.
    """

    try:
        with open(runtime_params_filepath, "r") as file:
            data = json.load(file)
            if not data:
                raise ValueError(f'[ERROR] Empty JSON file "{runtime_params_filepath}". Please check the contents.')
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f'[ERROR] Invalid JSON structure in "{runtime_params_filepath}".\nDetails: {e}')
    except Exception as e:
        raise RuntimeError(f'[ERROR] Unable to read "{runtime_params_filepath}". Details: {e}')

def get_runtime_variable(
    name: str,
    required: bool = False
) -> Optional[str]:
    """
    Retrieve an environment variable safely, handling missing or empty values.

    This function fetches an environment variable and logs a warning if a required
    variable is missing or empty.

    Args:
        name (str): The name of the environment variable to retrieve.
        required (bool, optional): Whether the variable is mandatory. Defaults to False.

    Raises:
        RuntimeError: If there is an issue retrieving the environment variable.

    Returns:
        Optional[str]: The value of the environment variable, or None if it is missing.

    Notes:
        - If `required=True` and the variable is missing, a warning is logged.
        - If an exception occurs, `RuntimeError` is raised.
    """

    try:
        value = os.getenv(name)
        if required and (value is None or value.strip() == ""):
            logging.warning(f'WARNING: Required parameter "{name}" is missing or empty.')
            return None
        return value
    except Exception as e:
        raise RuntimeError(f'ERROR: Unable to load environment variable "{name}". Details: {e}')

def validate_runtime_params(
    runtime_params_filepath
):
    """
    Validates the existence and content of the runtime parameters JSON file.

    This function checks whether the specified JSON file exists, is not empty,
    and contains valid JSON. It raises appropriate exceptions if any of the
    validation steps fail.

    Args:
        runtime_params_filepath (str or Path): The file path to the runtime parameters JSON file
                                               that needs to be validated.

    Raises:
        FileNotFoundError: If the file specified by `runtime_params_filepath` does not exist.
        ValueError: If the file is empty or if it does not contain valid JSON.

    Notes:
        - This function reads the file as a string, strips any leading or trailing whitespace,
          and checks for content.
        - The function ensures that the file contains valid JSON. If the file is malformed
          or contains invalid JSON, a `ValueError` will be raised.
        - If the file does not exist, a `FileNotFoundError` will be raised.

    Example:
        >>> validate_runtime_params("/path/to/runtime-params.json")
        >>> # Raises ValueError if the file is empty or contains invalid JSON,
        >>> # Raises FileNotFoundError if the file doesn't exist.
    """

    if not os.path.exists(runtime_params_filepath):
        raise FileNotFoundError(f"{runtime_params_filepath} not found.")

    with open(runtime_params_filepath, 'r') as file:
        content = file.read().strip()
        if not content:
            raise ValueError(f"{runtime_params_filepath} is empty.")
        try:
            json.loads(content)  # Check if it's valid JSON
        except json.JSONDecodeError:
            raise ValueError(f"{runtime_params_filepath} contains invalid JSON.")

## Ensure runtime_params_filepath file exists, create it based on system-params file if missing
if not runtime_params_filepath.exists():
    try:
        # Check multiple filepaths efficiently
        missing_files = [path for path in [project_params_filepath, default_params_filepath] if not path.exists()]
        if missing_files:
            missing_filenames = ", ".join(str(path) for path in missing_files)
            raise FileNotFoundError(f'ERROR: The following files are missing: {missing_filenames}.')

        arguments_data = load_json_sources([str(path) for path in system_params_listing], mode="merge")

        # initial_defaults = {details["target_env"]: details.get("default", "") for key, details in arguments_data.items() if "target_env" in details}
        initial_defaults = {
            details["target_env"]: details.get("default", "")
            for key, details in arguments_data.items()
            if "target_env" in details
        }

        with open(runtime_params_filepath, "w") as file:
            json.dump(initial_defaults, file, indent=4)

        # if runtime_params_filepath.exists():  # Ensure the file was actually created
        #     logging.info(f'Successfully created {runtime_params_filename} using sources: {", ".join(str(path.relative_to(project_root)) for path in system_params_listing)}.')
        # else:
        #     logging.info(f'Unable to create {runtime_params_filename} missing sources: {", ".join(str(path.relative_to(project_root)) for path in system_params_listing)}.')
        status = "Successfully created" if runtime_params_filepath.exists() else "Unable to create"
        sources = ", ".join(str(path.relative_to(project_root)) for path in system_params_listing)
        logging.info(f'{status} {runtime_params_filename} using sources: {sources}.')

    except Exception as e:
        logging.critical(f'ERROR: Unable to create {runtime_params_filename}. Details: {e}')
        sys.exit(1)
else:
    with open(runtime_params_filepath, "w") as file:
        file.write("{}")  # Overwrite with an empty JSON object
    logging.info(f'Flushed {runtime_params_filepath} to ensure a fresh structure.')

## Run configure_params() first to generate runtime-params file
try:

    SYSTEM_PARAMS, RUNTIME_PARAMS = configure_params()
    # if not isinstance(RUNTIME_PARAMS, dict) or not all(isinstance(RUNTIME_PARAMS.get(section, {}), dict) for section in RUNTIME_PARAMS):
    #     logging.critical("ERROR: configure_params() did not return a dictionary with expected sections.")
    #     sys.exit(1)

    # Add logging to inspect the structure of RUNTIME_PARAMS
    logging.debug(f"Run-Time Parameters: {RUNTIME_PARAMS}")  # This will log the structure of RUNTIME_PARAMS

    # Check if the RUNTIME_PARAMS object is empty or missing expected keys before proceeding
    if not RUNTIME_PARAMS or not isinstance(RUNTIME_PARAMS, dict):
        logging.warning(
            f'[WARNING] RUNTIME_PARAMS is empty or not structured as expected, skipping further processing.'
        )
    else:
        ## Extract runtime variables dynamically

        # SECTIONS_VARS = {
        #     section: {
        #         key: value.get("default")
        #         for key, value in section_data.get("options", {}).items()
        #     }
        #     for section, section_data in RUNTIME_PARAMS.items()
        # }
        # print( f'Sections Vars type:', type(SECTIONS_VARS))
        # print( f'Section Vars: {SECTIONS_VARS}' )

        SECTIONS_VARS = {
            section: {
                key: value.get("default") if isinstance(value, dict) else value
                for key, value in section_data.get("options", {}).items() if isinstance(section_data, dict)
            }
            for section, section_data in RUNTIME_PARAMS.items()
        }

    # # Set environment variables for all sections
    # for section_name, section_vars in SECTIONS_VARS.items():
    #     for key, value in section_vars.items():
    #         os.environ[key] = str(value)
    #         print( f'OS Environment [{key}] = {os.environ[key]}' )
    # # Update the missing variables check
    # required_vars = SECTIONS_VARS.get("REQUIRED", {})
    # missing_vars = [var for var in required_vars if not os.environ.get(var)]
    # if missing_vars:
    #     logging.critical(f'CRITICAL ERROR: Missing required environment variables: {", ".join(missing_vars)}')
    #     sys.exit(1)
    # # ## Debug mode conversion
    # # if "DEBUG" in os.environ:
    # #     os.environ["DEBUG"] = str(os.environ["DEBUG"].lower() == "true")
    # # if "VERBOSE" in os.environ:
    # #     os.environ["VERBOSE"] = str(os.environ["VERBOSE"].lower() == "true")

except Exception as e:
    logging.critical(f'[ERROR] Exception occurred while running configure_params: {e}')
    # sys.exit(1)
# ## Logging final merged configuration
# logging.info("Default's merged configuration (RUNTIME_VARS):")
# logging.info(json.dumps(defaults, indent=4))
