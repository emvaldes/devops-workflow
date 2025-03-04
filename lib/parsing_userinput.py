#!/usr/bin/env python3

# File: ./lib/parsing_userinput.py
# Version: 0.1.0

"""
File: ./lib/parsing_userinput.py

Description:
    User Input Collection and Interactive Prompts
    This module ensures all required runtime parameters are provided by prompting users interactively.
    It dynamically loads argument configurations, identifies missing variables, and sets
    environment variables accordingly.

Core Features:
    - **Interactive Input Requests**: Prompts users for required input dynamically.
    - **Configuration-Based Prompts**: Loads argument configurations from a JSON file.
    - **Environment Variable Management**: Updates system environment variables at runtime.
    - **Error Handling**: Ensures non-interactive environments exit safely with meaningful errors.

Usage:
    To collect required user input:
    ```bash
    python parsing_userinput.py
    ```

Dependencies:
    - json
    - os
    - logging

Global Variables:
    - Environment variables are dynamically updated based on user input.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to missing input in a non-interactive environment.

Example:
    ```bash
    python parsing_userinput.py
    ```
"""

import sys
import json
import os
import logging

# # Configure logging for debugging purposes
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

def request_input(
    prompt: str,
    required: bool = True,
    default: str = None
) -> str:
    """
    Prompt the user for input with an optional default value.

    This function requests input from the user in an interactive session. If running
    in a non-interactive environment, it logs an error and exits.

    Args:
        prompt (str): The message displayed to the user.
        required (bool, optional): Whether the input is mandatory. Defaults to True.
        default (str, optional): The default value if no input is provided. Defaults to None.

    Raises:
        SystemExit: If required input is missing in a non-interactive environment.
        KeyboardInterrupt: If the user manually interrupts input.

    Returns:
        str: The user-provided input or the default value.

    Notes:
        - If `sys.stdin.isatty()` is `False`, the function logs an error and exits, as interactive input is not possible.
        - If the user presses Ctrl+C, the function logs the interruption and exits.
    """

    if not sys.stdin.isatty():
        logging.error(f'ERROR: Required parameter "{prompt}" is missing and cannot be requested in a non-interactive environment.')
        print(f'ERROR: Required parameter "{prompt}" is missing and cannot be requested in a non-interactive environment.')
        exit(1)
    try:
        while True:
            user_input = input(f'{prompt} [{default}]: ' if default else f'{prompt}: ').strip()
            if user_input:
                logging.debug(f'User input received for {prompt}: {user_input}')
                return user_input
            if not required:
                return default
            print("This field is required. Please enter a value.", end="\r")
    except KeyboardInterrupt:
        logging.critical("Input interrupted by user. Exiting cleanly.")
        print("\nERROR: Input interrupted by user. Exiting cleanly.")
        exit(1)

def user_interview(
    arguments_config: dict,
    missing_vars: list
) -> dict:
    """
    Collect required user input for missing environment variables.

    Iterates through the list of missing environment variables and prompts the user
    for their values based on the argument configuration.

    Args:
        arguments_config (dict): Dictionary containing argument configurations.
        missing_vars (list): List of required variables that are missing.

    Returns:
        dict: A dictionary mapping missing variable names to user-provided values.

    Notes:
        - This function cross-references `arguments_config` to determine the prompt and default values.
        - Calls `request_input()` for each missing variable.
        - The returned dictionary contains user-provided inputs mapped to their respective variables.
    """

    user_inputs = {}
    for var in missing_vars:
        for param, details in arguments_config.items():
            if details.get("target_env") == var:
                prompt_message = details.get("prompt", f'Enter value for {var}')
                default_value = details.get("default", "")
                logging.debug(f'Prompting user for: {var} - Default: {default_value}')
                user_inputs[var] = request_input(prompt_message, required=True, default=default_value)
    return user_inputs

def parse_and_collect_user_inputs(
    arguments_config_path: str,
    required_runtime_vars: list
) -> dict:
    """
    Load argument configuration, identify missing variables, and prompt the user.

    Reads structured argument definitions from a JSON file, checks for missing
    environment variables, and interacts with the user if required.

    Args:
        arguments_config_path (str): Path to the JSON configuration file.
        required_runtime_vars (list): List of required runtime variables.

    Raises:
        FileNotFoundError: If the argument configuration file is missing.

    Returns:
        dict: A dictionary of user-provided environment variable values.

    Notes:
        - If the configuration file is missing, logs an error and raises `FileNotFoundError`.
        - Identifies missing variables by checking against environment variables.
        - Calls `user_interview()` for interactive input collection.
        - Updates `os.environ` dynamically based on user input.
    """

    if not os.path.exists(arguments_config_path):
        logging.critical(f'ERROR: Arguments configuration file not found at {arguments_config_path}')
        raise FileNotFoundError(f'ERROR: Arguments configuration file not found at {arguments_config_path}')
    logging.debug(f'Loading arguments configuration from: {arguments_config_path}')
    with open(arguments_config_path, "r") as file:
        arguments_config = json.load(file)
    logging.debug(f'Arguments configuration loaded: {json.dumps(arguments_config, indent=4)}')
    missing_vars = [var for var in required_runtime_vars if not os.getenv(var)]
    logging.info(f'Missing required environment variables: {missing_vars}')
    if missing_vars:
        logging.info("Some required parameters are missing. Initiating user-interview process.")
        user_inputs = user_interview(arguments_config, missing_vars)
        for key, value in user_inputs.items():
            os.environ[key] = str(value)
            logging.debug(f'Environment variable set: {key} = {value}')
        return user_inputs
    logging.info("No missing required environment variables. Proceeding without user interaction.")
    return {}

def main() -> None:
    """
    Main entry point for parsing user input and managing runtime parameters.

    This function:
    - Loads the argument configuration from a JSON file.
    - Identifies missing required runtime variables.
    - Prompts the user interactively to collect missing values.
    - Updates environment variables dynamically.

    Raises:
        FileNotFoundError: If the argument configuration file is missing.
        Exception: If an unexpected error occurs during execution.

    Returns:
        None: This function does not return any values; it manages user input handling.

    Workflow:
        1. Defines the path to the argument configuration file.
        2. Identifies missing runtime parameters that need user input.
        3. Calls `parse_and_collect_user_inputs()` to process required variables.
        4. Logs the collected user input and updates environment variables dynamically.

    Notes:
        - If a required argument configuration file is missing, execution is halted.
        - If running in a **non-interactive** environment, the script exits safely.
    """

    pass

if __name__ == "__main__":
    main()
