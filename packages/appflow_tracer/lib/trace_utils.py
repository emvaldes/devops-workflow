#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/trace_utils.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system module
import sys

# Standard library imports - Utility modules
import json
import inspect
import logging

# Standard library imports - Type-related modules
from types import FrameType
from typing import Callable

# Standard library imports - File system-related module
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from . import (
    log_utils,
    file_utils,
    serialize_utils
)

# Import category from system_variables
from lib.system_variables import (
    category
)

def start_tracing(
    logger: logging.Logger = None,
    configs: dict = None
) -> None:

    # Initialize logger (logging.Logger) if None
    if logger is None:
        logger = logging.getLogger("trace_utils")

    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    if not configs or "logging" not in configs:
        print("⚠️ Warning: configs is not properly initialized in trace_all.")
        # return None  # This leads to the error
        return lambda frame, event, arg: None  # A no-op trace function
    # print(f'Configs: {configs}')

    # print(f'Trace All result: {trace_all(configs)}')
    # print(f'Trace All type: {type(trace_all(configs))}')

    if configs["tracing"].get("enable", True) and sys.gettrace() is None:  # Prevent multiple traces
        trace_func = trace_all(logger=logger, configs=configs)
        if trace_func is None:
            print("Trace function is None, skipping tracing.")
            return
        # sys.settrace(lambda frame, event, arg: trace_all(configs)(frame, event, arg))
        sys.settrace(lambda frame, event, arg: trace_func(frame, event, arg))
    # message = f'Start Tracing invoked!'
    # log_utils.log_message(message, category.calls.id, configs=configs)

def trace_all(
    logger: logging.Logger,
    configs: dict
) -> Callable:

    # Ensure configs is valid before using it
    if not configs or "logging" not in configs:
        print("⚠️ Warning: configs is not properly initialized in trace_all.")
        return None  # Stop tracing if configs is not ready
    # print( f'Configs: {configs}' )

    # Ensure the logger is properly initialized
    # global logger

    def trace_events(
        frame: FrameType,
        event: str,
        arg: object
    ) -> None:

        # print(f'\nTracing activated in {__name__}\n')

        # Define functions to be ignored
        excluded_functions = {"emit", "log_utils.log_message"}
        if frame.f_code.co_name in excluded_functions:
            return  # Skip tracing these functions

        # # Excluding non-project specific sources
        # filename = frame.f_globals.get("__file__", "")
        # if not file_utils.is_project_file(filename):
        #     # print(f'Excluding: {filename}')
        #     return None  # Stop tracing for non-project files

        try:
            # Excluding non-project specific sources
            filename = frame.f_globals.get("__file__", "")
            if not filename:
                # If filename is None or an empty string, skip further processing
                return None
            if not file_utils.is_project_file(filename):
                # print(f'Excluding: {filename}')
                return None  # Stop tracing for non-project files
            # Additional logic can follow here, like calling file_utils.is_project_file(filename)
        except (TypeError, ValueError):
            # Handle None or unexpected inputs gracefully
            return None

        # print( f'Event: {event}' )
        # print( f'\nLogger: {logger}' )
        # print( f'\nFrame: {frame}' )
        # print( f'\nFilename: {filename}' )
        # print( f'\nArg: {arg}' )
        # print( f'Configs: {configs}\n' )

        if event == category.calls.id.lower():
            call_events(
                logger=logger,
                frame=frame,
                filename=filename,
                arg=arg,
                configs=configs
            )
        elif event == category.returns.id.lower():
            return_events(
                logger=logger,
                frame=frame,
                filename=filename,
                arg=arg,
                configs=configs
            )

        return trace_events  # trace_events function (Continue tracing)

    return trace_events      # trace_all function (Return Function)

def call_events(
    logger: logging.Logger,
    frame: FrameType,
    filename: str,
    arg: object,
    configs: dict
) -> None:

    try:

        log_category = category.calls.id
        print_event = configs["events"].get(category.calls.id.lower(), False)
        message = ""  # Initialize message early

        caller_frame = frame.f_back  # Get caller frame
        if caller_frame:

            caller_info = inspect.getframeinfo(caller_frame)
            caller_filename = file_utils.relative_path(caller_info.filename)  # Convert absolute path to relative
            invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
            invoking_line = serialize_utils.sanitize_token_string(invoking_line)
            # {file_utils.relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]"

            message = f'\n[{log_category}] {caller_filename} ( {invoking_line} )'.strip()
            if print_event:
                log_utils.log_message(message, log_category, configs=configs)

            if caller_frame.f_code.co_name == "<module>":
                caller_lineno = caller_info.lineno
                caller_module = caller_filename if "/" not in caller_filename else caller_filename.split("/")[-1]
                message  = f'[{log_category}] {caller_module}[{caller_lineno}] ( {invoking_line} ) '
                message += f'-> {file_utils.relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]'
                if print_event:
                    log_utils.log_message(message.strip(), log_category, configs=configs)

            else:
                caller_co_name = caller_frame.f_code.co_name
                callee_info = inspect.getframeinfo(frame)
                arg_values = inspect.getargvalues(frame)
                arg_list = {arg: arg_values.locals[arg] for arg in arg_values.args}
                message  = f'[{log_category}] {caller_filename} ({caller_co_name})[{caller_info.lineno}] '
                message += f'-> {file_utils.relative_path(callee_info.filename)} ({frame.f_code.co_name})[{callee_info.lineno}]'
                # Fix: Ensure JSON serialization before passing data
                try:
                    arg_list = json.loads(json.dumps({arg: arg_values.locals[arg] for arg in arg_values.args}, default=str))
                except (TypeError, ValueError):
                    arg_list = "[Unserializable data]"
                if print_event:
                    log_utils.log_message(message.strip(), log_category, json_data=arg_list, configs=configs)

    except Exception as e:
        logger.error(f'Error in trace_all: {e}')

def return_events(
    logger: logging.Logger,
    frame: FrameType,
    filename: str,
    arg: object,
    configs: dict
) -> None:

    try:

        log_category = category.returns.id
        print_event = configs["events"].get(category.returns.id.lower(), False)
        message = ""  # Initialize message early

        return_filename = file_utils.relative_path(filename)
        return_lineno = frame.f_lineno
        return_type = type(arg).__name__

        # Inspecting return_value (dict)
        # {
        #     "success": bool,
        #     "serialized": data,
        #     "type": type
        # }
        # return_value = serialize_utils.safe_serialize(arg)  # Ensure JSON serializability
        serialized_result = serialize_utils.safe_serialize(
            data=arg,
            configs=configs
        )
        if serialized_result["success"]:
            return_value = serialized_result["serialized"]  # Use the properly serialized string
        else:
            return_value = f'[Unserializable: {serialized_result["type"]}] Error: {serialized_result.get("error", "Unknown")}'
        # message  = f'\n[RETURN] {return_filename}[{return_lineno}] '
        # message += f'-> RETURN VALUE (Type: {return_type}): {return_value}'
        # , "RETURN", configs=configs)

        # Get the returning module/function name
        if frame.f_code.co_name == "<module>":
            return_filename = file_utils.relative_path(frame.f_globals.get("__file__", ""))
            return_co_name = return_filename  # Use filename instead of <module>
        else:
            return_co_name = frame.f_code.co_name

        # Capture the exact line of code causing the return
        return_info = inspect.getframeinfo(frame)
        return_lineno = return_info.lineno
        # Extract the actual return statement (if available)
        return_line = return_info.code_context[0] if return_info.code_context else "Unknown"
        return_line = serialize_utils.sanitize_token_string(return_line)  # Clean up comments and spaces

        # Print the type of the return value and inspect its structure
        arg_type = type(arg).__name__
        # If it's an argparse.Namespace or other complex object, print its full structure
        # Check if it's a complex object (e.g., argparse.Namespace)
        if hasattr(arg, "__dict__"):
            return_value = vars(arg)  # Convert Namespace or similar object to a dictionary
        elif arg is None:  # Correct way to check for NoneType
            return_value = None
        elif isinstance(arg, bool):  # Ensures booleans remain as True/False
            return_value = arg  # Keep as boolean
            # print(f'Return Value (Boolean): {return_value}')
        else:
            return_value = arg  # Keep original

        message  = f'[{log_category}] {return_filename}[{return_lineno}] ( {return_line} ) '
        if return_value in [None, "null", ""] or isinstance(return_value, bool):
            message += f'-> {arg_type}: {return_value}'
        else:
            message += f'-> {arg_type}:'

        if print_event:
            log_utils.log_message(message.strip(), log_category, json_data=return_value, configs=configs)

    # except Exception:
    #     pass  # Ignore frames that cannot be inspected
    except Exception as e:
        logger.error(f'Error in trace_all return handling: {e}')

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
