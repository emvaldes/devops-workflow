#!/usr/bin/env python3

"""
File Path: ./lib/configure_params.py

Description:

Configuration Parameters Manager

This module is responsible for loading, validating, and managing configuration parameters.
It integrates with the framework's parameter handling system, merging user-defined and default settings.

Core Features:

- **JSON Configuration Loading**: Reads structured parameters from system configuration files.
- **Runtime Parameter Management**: Dynamically integrates `.env` values into execution logic.
- **Validation & Error Handling**: Ensures required configuration files exist and are correctly formatted.
- **Automatic Environment Initialization**: Creates missing `.env` and `runtime-params.json` when necessary.

Primary Functions:

- `load_json_sources(filepaths, mode)`: Loads and merges JSON configuration files.
- `fetching_runtime_variables()`: Retrieves structured runtime parameters.
- `initialize_env_file()`: Ensures `.env` exists and is valid.
- `initialize_runtime_file()`: Ensures `runtime-params.json` is properly set up.
- `populate_env_file()`: Writes environment variables dynamically.
- `populate_runtime_file()`: Generates structured runtime parameters.

Expected Behavior:

- If a required configuration file is missing, an error is logged.
- JSON parsing errors are handled gracefully to prevent execution failures.
- `.env` is updated dynamically when runtime parameters are changed.

Dependencies:

- `json`, `os`, `logging`, `dotenv`
- `system_variables` (for directory paths and project settings)

Usage:

To process and validate configuration parameters:
> python configure_params.py
"""

import sys
import os

import logging
import json

from pathlib import Path
from dotenv import load_dotenv, dotenv_values

from typing import List, Dict, Tuple, Union

from system_variables import (
    project_root,
    env_filepath,
    runtime_params_filename,
    system_params_filename,
    runtime_params_filepath,
    system_params_filepath,
    system_params_listing
)

env_file_header = "## Environment variables (auto-generated)\n\n"

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def load_json_sources(
    filepaths: List[str],
    mode: str = "merge"
) -> Union[Dict, Tuple[Dict]]:
    """
    Loads JSON configuration files and merges them or returns them separately.

    This function reads multiple JSON files and either merges them into a single dictionary
    (`merge` mode) or returns them separately as a tuple of dictionaries (`fetch` mode).

    Args:
        filepaths (List[str]): A list of JSON file paths to load.
        mode (str, optional): Determines the return format. Either "merge" (default) or "fetch".

    Raises:
        ValueError: If a JSON file is not structured as a dictionary.
        ValueError: If the JSON structure is invalid.
        RuntimeError: If there's an issue reading the file.

    Returns:
        Union[Dict, Tuple[Dict]]: Merged dictionary or a tuple of dictionaries.
    """

    json_data = []
    merged_data = {}
    for filepath in filepaths:
        try:
            with open(filepath, "r") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError(f"ERROR: JSON file '{filepath}' must contain an object at the root level.")
                json_data.append(data)
                merged_data.update(data)  # Merge the content
        except json.JSONDecodeError as e:
            raise ValueError(f"ERROR: Invalid JSON structure in '{filepath}'.\nDetails: {e}")
        except Exception as e:
            raise RuntimeError(f"ERROR: Unable to read '{filepath}'. Details: {e}")
    return tuple(json_data) if mode == "fetch" else merged_data
# # Example call
# if __name__ == "__main__":
#     filepaths = ["config1.json", "config2.json"]  # List of JSON files to load
#
#     # Fetch mode: Get each JSON file separately as tuples
#     json_tuple = load_json_sources(filepaths, mode="fetch")
#
#     # Merge mode: Combine all JSON files into one dictionary
#     merged_config = load_json_sources(filepaths, mode="merge")

# def fetching_runtime_variables():
#     """Retrieve a dictionary of all target_env values categorized by section."""
#     try:
#         expected_path = system_params_filepath.resolve()
#         logging.info(f"Looking for {system_params_filename} at: {expected_path}")
#         if not system_params_filepath.exists():
#             logging.critical(f"{system_params_filepath} file is missing. Expected at: {expected_path}")
#             sys.exit(1)
#         with open(system_params_filepath, "r") as json_file:
#             system_params_json = json.load(json_file)
#         runtime_vars = {}
#         for section, section_data in system_params_json.items():
#             section_title = section_data.get("title", section)
#             section_options = section_data.get("options", {})
#             # Ensure section_options is a dictionary before processing
#             if not isinstance(section_options, dict):
#                 raise TypeError(f"Expected a dictionary for 'options' in section {section}, but got {type(section_options).__name__}")
#             # runtime_vars[section.upper()] = {
#             runtime_vars[section] = {
#                 "title": section_title,
#                 "options": {key: details.get("default", "") for key, details in section_options.items() if isinstance(details, dict)}
#             }
#         # logging.info(f"Extracted runtime vars: {runtime_vars}")
#         return runtime_vars
#     except Exception as e:
#         logging.error(f"Error retrieving runtime variables: {e}")
#         sys.exit(1)

def fetching_runtime_variables() -> Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
    """
    Retrieve runtime variables categorized by section.

    Loads structured system parameters and extracts `target_env` values categorized by section.

    Raises:
        TypeError: If `options` inside a section is not a dictionary.
        SystemExit: If an error occurs during retrieval.

    Returns:
        Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
        A dictionary mapping section names to their titles and option key-value pairs.
    """

    try:
        # expected_path = system_params_filepath.resolve()
        # logging.info(f"Looking for {system_params_filename} at: {expected_path}")
        # if not system_params_filepath.exists():
        #     logging.critical(f"{system_params_filepath} file is missing. Expected at: {expected_path}")
        #     sys.exit(1)
        # Use load_json_sources instead of manually opening the file
        system_params_json = load_json_sources([str(path) for path in system_params_listing], mode="merge")
        runtime_vars = {}
        for section, section_data in system_params_json.items():
            section_title = section_data.get("title", section)
            section_options = section_data.get("options", {})
            # Ensure section_options is a dictionary before processing
            if not isinstance(section_options, dict):
                raise TypeError(f"Expected a dictionary for 'options' in section {section}, but got {type(section_options).__name__}")
            runtime_vars[section] = {
                "title": section_title,
                "options": {key: details.get("default", "") for key, details in section_options.items() if isinstance(details, dict)}
            }
        return runtime_vars
    except Exception as e:
        logging.error(f"Error retrieving runtime variables: {e}")
        sys.exit(1)

def initialize_env_file():
    """
    Ensure the `.env` file exists and contains valid content.

    If the file is missing or invalid, it will be recreated and populated.

    Raises:
        SystemExit: If the `.env` file cannot be populated.
    """

    try:
        if not validate_env_file():
            logging.info(".env file is missing or invalid. Recreating and populating it.")
            if not populate_env_file():
                logging.critical(f'Failed to populate .env due to missing {system_params_filepath}. Execution halted.')
                sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to initialize .env file: {e}")
        sys.exit(1)

def initialize_runtime_file():
    """
    Ensure the `runtime-params.json` file exists and contains valid content.

    If the file is missing or invalid, it will be recreated and populated.

    Raises:
        SystemExit: If the `runtime-params.json` file cannot be populated.
    """

    try:
        if not validate_runtime_file():
            logging.info(f'{runtime_params_filename} file is missing or invalid. Recreating and populating it.')
            if not populate_runtime_file():
                logging.critical(f'Failed to populate {runtime_params_filename} due to missing {system_params_filepath}. Execution halted.')
                sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to initialize {runtime_params_filename} file: {e}")
        sys.exit(1)

def populate_env_file() -> bool:
    """
    Writes environment variables dynamically to the `.env` file.

    Retrieves structured runtime parameters and formats them for `.env` storage.

    Raises:
        Exception: If there is an error during file population.

    Returns:
        bool: True if the `.env` file is successfully populated and validated, False otherwise.
    """

    try:
        runtime_vars = fetching_runtime_variables()
        # print( f'RunTime Variables:\n{runtime_vars}' )
        with open(env_filepath, "w") as env_file:
            for section, section_data in runtime_vars.items():
                # Use the "title" field if available, or fall back to the section name
                section_title = section_data.get("title", section)
                logging.debug(f"Using section [ {section_title} ]")
                env_file.write(f"## {section_title}\n")
                for key, value in section_data.get("options", {}).items():
                    env_file.write(f"{key}={value}\n")
                env_file.write("\n")
        logging.info(".env file populated with environment variables.")
        return validate_env_file()
    except Exception as e:
        logging.error(f"Error populating .env file: {e}")
        return False

def populate_runtime_file() -> bool:
    """
    Generates structured runtime parameters by merging system parameters with `.env` values.

    Updates `runtime-params.json` by:
    - Extracting runtime variables.
    - Merging environment variables.
    - Removing unnecessary titles.

    Raises:
        SystemExit: If the runtime parameters cannot be initialized.

    Returns:
        bool: True if `runtime-params.json` is successfully updated, False otherwise.
    """

    try:
        runtime_vars = fetching_runtime_variables()
        # Load existing environment values
        env_values = dotenv_values(env_filepath)
        # Dynamically update all sections
        for section, section_data in runtime_vars.items():
            for key in section_data.get("options", {}):
                if key in env_values:
                    section_data["options"][key] = env_values[key]
        # Remove titles from each section
        for section_data in runtime_vars.values():
            # if "title" in section_data:
            #     del section_data["title"]
            section_data.pop("title", None)
        # Write the updated runtime_vars to the runtime-params file
        with open(runtime_params_filepath, "w") as file:
            json.dump(runtime_vars, file, indent=4)
        # logging.info(f'Updated {runtime_params_filename} file with structured environment variables from {', '.join(str(path.relative_to(project_root)) for path in system_params_listing)} and .env files.')
        sources = ", ".join(str(path.relative_to(project_root)) for path in system_params_listing)
        logging.info(f"Updated '{runtime_params_filename}' with env variables from {sources} and .env files.")
        return True
    except Exception as e:
        logging.critical(f"ERROR: Unable to initialize {runtime_params_filename} config file. Details: {e}")
        sys.exit(1)

def validate_env_file() -> bool:
    """
    Validate the existence and integrity of the `.env` file.

    Ensures that the `.env` file exists and contains valid content. If the file is empty
    or only contains a header, it is considered invalid.

    Returns:
        bool: True if the file exists and is valid, False otherwise.
    """

    try:
        if not env_filepath.exists():
            logging.warning(".env file does not exist.")
            return False
        with open(env_filepath, "r") as env_file:
            content = env_file.read().strip()
            logging.info(f".env file content:\n{content}")
            if content == "" or content == env_file_header.strip():
                logging.warning(".env file exists but is invalid (empty or only contains the header).")
                return False
        return True
    except Exception as e:
        logging.error(f"Error validating .env file: {e}")
        return False

def validate_runtime_file() -> bool:
    """
    Validate the existence and integrity of the `runtime-params.json` file.

    Ensures that the `runtime-params.json` file exists and contains valid content.
    If the file is empty or contains an invalid structure, it is considered invalid.

    Returns:
        bool: True if the file exists and is valid, False otherwise.
    """

    try:
        if not runtime_params_filepath.exists():
            logging.warning(f'{runtime_params_filename} file does not exist."')
            return False
        with open(runtime_params_filepath, "r") as runtime_params_file:
            content = runtime_params_file.read().strip()
            logging.info(f'{runtime_params_filename} content:{content}')
            if content == "" or content == '{}':
                logging.warning(f'{runtime_params_filename} file exists but is invalid (empty or only contains the header).')
                return False
        return True
    except Exception as e:
        logging.error(f"Error validating .env file: {e}")
        return False

def main() -> Tuple[Dict, Dict]:
    """
    Processes environment configurations by integrating `.env` with `runtime-params.json`.

    This function:
    - Ensures `.env` and `runtime-params.json` exist and are valid.
    - Loads system parameters and runtime parameters.

    Raises:
        Exception: If an error occurs while processing environment configurations.

    Returns:
        Tuple[Dict, Dict]: A tuple containing system parameters and runtime parameters.
    """

    try:
        initialize_env_file()
        initialize_runtime_file()
        load_dotenv(env_filepath)
        ## Fetching Runtime-Params file
        with open(runtime_params_filepath, "r") as file:
            runtime_params = json.load(file)
        # ## Fetching System-Params file
        # with open(system_params_filepath, "r") as file:
        #     system_params = json.load(file)
        system_params = load_json_sources([str(path) for path in system_params_listing], mode="merge")
        return system_params, runtime_params
    except Exception as e:
        logging.error(f"Error processing environment configuration: {e}")
        return {}

if __name__ == "__main__":
    main()

# def initialize_runtime_params__deprecated():
#     """Ensure runtime-params file exists. If missing, create it. Then wipe and update it with .env values."""
#     try:
#         if not runtime_params_filepath.exists():
#             with open(runtime_params_filepath, "w") as file:
#                 json.dump({}, file, indent=4)
#             logging.info(f"Created missing {runtime_params_filepath}.")
#
#         with open(runtime_params_filepath, "w") as file:
#             json.dump({}, file, indent=4)
#         logging.info(f'Wiped existing {runtime_params_filename} config file before updating.')
