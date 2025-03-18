#!/usr/bin/env python3

# File: ./packages/appflow_tracer/tracing.py

__package__ = "packages.appflow_tracer"
__module__ = "tracing"

__version__ = "0.1.0"  ## Package version

#-------------------------------------------------------------------------------

# Standard library imports - Core system module
import sys

# Standard library imports - Built-in utilities
import builtins
import warnings

# Standard library imports - Utility modules
import json
import inspect
import logging

# Standard library imports - Date and time handling
from datetime import datetime

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Type hinting (kept in a separate group)
from typing import Optional, Union

#-------------------------------------------------------------------------------

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

#-------------------------------------------------------------------------------

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs,
    default_indent
)
# Import trace_utils from lib.*_utils
from .lib import (
    file_utils,
    log_utils,
    trace_utils
)
from lib import (
    pkgconfig_loader as pkgconfig
)

#-------------------------------------------------------------------------------

def setup_logging(
    configs: Optional[dict] = None,
    logname_override: Optional[str] = None,
    events: Optional[Union[bool, dict]] = None
) -> Union[bool, dict]:

    # Ensure the variable exists globally
    global LOGGING, CONFIGS, logger
    try:
        if not LOGGING:  # Check if logging has already been initialized
            LOGGING = True  # Mark logging as initialized
            # print(f'\nInitializing Setup Logging ... \n')
    except NameError:
        return False
    if logname_override:
        log_filename = logname_override
    # Inspect the stack to find the caller’s module name or file
    caller_frame = inspect.stack()[1]
    # Determine the caller's module or file
    caller_module = inspect.getmodule(caller_frame[0])
    if caller_module and caller_module.__file__:
        # Extract the script/module name without extension
        log_filename = Path(caller_module.__file__).stem
    else:
        # Fallback if the name can’t be determined
        log_filename = "unknown"
    # Handle the case where __main__ is used
    if log_filename == "__main__":
        # Use the module that defines setup_logging as a fallback
        current_frame = inspect.currentframe()
        this_module = inspect.getmodule(current_frame)
        if this_module and this_module.__file__:
            log_filename = Path(this_module.__file__).stem
        else:
            # Fallback if the name can’t be determined
            log_filename = "default"
    absolute_path = None
    # Construct the full log path separately
    if caller_module and caller_module.__file__:
        caller_path = Path(caller_module.__file__).resolve()
        absolute_path = caller_path.with_name(log_filename)
        if caller_path.is_relative_to(project_root):
            # If the caller is within project_root, construct a relative log path
            relative_path = caller_path.relative_to(project_root)
            log_filename = relative_path.parent / f'{log_filename}'
        else:
            # If the caller is outside project_root, just use its absolute path under logs
            log_filename = caller_path.parent.relative_to(caller_path.anchor) / f'{log_filename}'
    # else:
    #     # If we couldn’t determine the caller file, fallback to a default
    #     log_filename = f'default'
    # Determining configs parameter
    if configs:
        CONFIGS = configs
    else:
        CONFIGS = pkgconfig.setup_configs(
            absolute_path=Path(absolute_path),
            logname_override=log_filename,
            events=events
        )
    if not isinstance(CONFIGS, dict):
        raise ValueError("Configs must be a dictionary")
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=default_indent)}' )
    logfile = CONFIGS["logging"].get("log_filename", False)
    logger = logging.getLogger(f'{CONFIGS["logging"]["package_name"]}.{CONFIGS["logging"]["module_name"]}')
    logger.propagate = False  # Prevent handler duplication
    logger.setLevel(logging.DEBUG)
    # Remove existing handlers before adding new ones (Prevents duplicate logging)
    if logger.hasHandlers():
        logger.handlers.clear()  # Ensure handlers are properly cleared before adding new ones
    else:
        # Use ANSIFileHandler as logfile handler
        file_handler = ANSIFileHandler(logfile, mode='a')
        logger.addHandler(file_handler)
        # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # file_handler.setFormatter(formatter)
        # file_handler.setLevel(logging.DEBUG)
        # Console handler (keeps ANSI color but ensures immediate output)
        console_handler = PrintCapture()
        logger.addHandler(console_handler)
        # console_handler.setFormatter(formatter)
        # console_handler.setLevel(logging.DEBUG)
    # Redirect print function statements to logger
    builtins.print = lambda *args, **kwargs: logger.info(" ".join(str(arg) for arg in args))
    # if CONFIGS["logging"].get("enable", False):
    #     builtins.print = lambda *args, **kwargs: sys.__stdout__.write(" ".join(str(arg) for arg in args) + "\n")
    # Ensure all logs are flushed immediately
    sys.stdout.flush()
    sys.stderr.flush()
    # if not LOGGING:  # Check if logging has already been initialized
    if CONFIGS["tracing"].get("enable", True):
        try:
            # start_tracing(CONFIGS)
            trace_utils.start_tracing(
                logger=logger,
                configs=CONFIGS
            )
            # log_utils.log_message("\nTracing system initialized.\n", "INFO", configs=CONFIGS)
        except NameError:
            return False
    # Manage log files before starting new tracing session
    file_utils.manage_logfiles(CONFIGS)
    return CONFIGS

#-------------------------------------------------------------------------------

class PrintCapture(logging.StreamHandler):

    #---------------------------------------------------------------------------
    # def emit(self, record):
    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
        sys.__stdout__.flush()  # Ensure immediate flushing
    # def emit(self, record):
    #     log_entry = self.format(record)
    #     sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
    #     sys.__stdout__.flush()  # Ensure immediate flushing

#-------------------------------------------------------------------------------

class ANSIFileHandler(logging.FileHandler):

    #---------------------------------------------------------------------------
    # def emit(self, record):
    def emit(self, record: logging.LogRecord) -> None:

        # Ensure only Python's internal logging system is ignored
        if "logging/__init__.py" in record.pathname:
            return  # Skip internal Python logging module logs
        super().emit(record)  # Proceed with normal logging

#-------------------------------------------------------------------------------

LOGGING = None
CONFIGS = None
logger = None  # Global logger instance

#-------------------------------------------------------------------------------

def main() -> None:

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible
    # Ensure logging is set up globally before anything else
    CONFIGS = setup_logging(events=["call", "return"])
    # CONFIGS = setup_logging(events={"call": True, "return": False})
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=default_indent)}' )

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

#-------------------------------------------------------------------------------

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()

# Debug: Read and display log content to verify logging works
# try:
#     log_file = CONFIGS["logging"].get("log_filename", False)
#     print( f'\nReading Log-file: {log_file}' )
#     with open(log_file, "r") as file:
#         # print("\nLog file content:")
#         print(file.read())
# except Exception as e:
#     print(f'Unable to read log file: {e}')
