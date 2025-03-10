#!/usr/bin/env python3

# File: ./lib/parsing_userinput.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system and OS interaction modules
import sys
import os

# Standard library imports - Utility modules
import json
import logging

# Standard library imports - File system-related module
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def request_input(
    prompt: str,
    required: bool = True,
    default: str = None
) -> str:

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
    pass

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
