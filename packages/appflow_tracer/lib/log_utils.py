#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/log_utils.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system module
import sys

# Standard library imports - Utility modules
import json  # If structured data is part of logging
import logging

# Standard library imports - Date and time handling
from datetime import datetime  # If timestamps are used or manipulated

# Standard library imports - File system-related module
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import category from system_variables
from lib.system_variables import (
    default_indent,
    category
)

# Determine the correct logging level dynamically
log_levels = {
    category.calls.id:    logging.INFO,
    category.returns.id:  logging.DEBUG,
    category.imports.id:  logging.WARNING,
    category.debug.id:    logging.DEBUG,
    category.info.id:     logging.INFO,
    category.warning.id:  logging.WARNING,
    category.error.id:    logging.ERROR,
    category.critical.id: logging.CRITICAL
}

def log_message(
    message: str,
    log_category: str = "INFO",
    json_data: dict = None,
    serialize_json: bool = False,
    configs: dict = None,
    handler: logging.Logger = None
) -> None:

    # configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    # print(f'log_message(configs): {json.dumps(configs, indent=default_indent, ensure_ascii=False)}')
    # Define logger if not available
    logger = handler or logging.getLogger(f'{configs["logging"]["package_name"]}.{configs["logging"]["module_name"]}')
    # print(f'Logger: {logger}')

    log_level = log_levels.get(log_category.upper(), logging.INFO)

    # If json_data exists, append it to the message
    if json_data:
        if serialize_json:
            json_data = json.dumps(json_data, separators=(",", ":"), ensure_ascii=False)

    if configs["logging"].get("enable", False) and not configs["tracing"].get("enable", False):
        if message.strip():
            output_logfile(logger, message, log_level, json_data or False)  # Write ONLY to log file if tracing is disabled

    if configs["tracing"].get("enable", False):
        if message.strip():
            output_console(message, log_category, json_data or False, configs)  # Write to console

def output_logfile(
    logger: logging.Logger,
    message: str,
    log_category: str = "INFO",
    json_data: dict = None
) -> None:

    logfile_message = f'{log_category}: {message}'

    # if json_data:
    #     logfile_message += f'\n{json_data}'
    if json_data:
        logfile_message += "\n" + json.dumps(json_data, separators=(',', ':'))  # Ensure proper JSON formatting

    # Disabling the removal of ANSI escape codes allowing end-users to see the original output experience.
    # message = file_utils.remove_ansi_escape_codes(message)
    logger.info(logfile_message)  # Write to log file

def output_console(
    message: str,
    log_category: str,
    json_data: dict = None,
    configs: dict = None
) -> None:

    color = configs["colors"].get(log_category.upper(), configs["colors"]["RESET"])
    if not color.startswith("\033"):  # Ensure it's an ANSI color code
        color = configs["colors"]["RESET"]
    console_message = f'{color}{message}{configs["colors"]["RESET"]}'
    print(console_message)  # Print colored message
    if json_data:
        compressed = configs["tracing"]["json"].get("compressed", None)
        # print(f'DEBUG: compressed={compressed} json_data={json_data}')  # Debugging output
        if compressed is not None:
            if isinstance(json_data, str):
                # Print strings as-is (no JSON formatting)
                print(json_data)
            else:
                if compressed:
                    print(json.dumps(json_data, separators=(",", ":"), ensure_ascii=False))
                else:
                    # Pretty-print JSON while keeping Unicode characters
                    print(json.dumps(json_data, indent=default_indent, ensure_ascii=False))

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
