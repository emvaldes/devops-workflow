#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/file_utils.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system module
import sys

# Standard library imports - Utility module
import re

# Standard library imports - File system-related module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs,
    max_logfiles,
    default_indent,
    category
)

from . import (
    log_utils
)

def is_project_file(
    filename: str
) -> bool:

    if not filename:
        # log_utils.log_message("is_project_file received None or empty filename.", category.info.id)
        return False
    try:
        filename_path = Path(filename).resolve()
        # log_utils.log_message("Resolved filename_path: {filename_path}", category.info.id)
        return project_root in filename_path.parents
    except (TypeError, ValueError):
        # Handle None or unexpected inputs gracefully
        return False

def manage_logfiles(
    configs: dict = None
) -> list:

    logs_dir = Path(configs["logging"]["logs_dirname"])  # Target the correct logs directory
    deleted_logs = []
    if not logs_dir.exists() or not logs_dir.is_dir():
        return deleted_logs  # If the log directory doesn't exist, return empty
    log_files = sorted(
        logs_dir.glob("*.log"),  # Only target logs in the configured directory
        key=lambda f: f.stat().st_mtime  # Sort by modification time (oldest first)
    )
    num_to_remove = len(log_files) - configs["logging"].get("max_logfiles", 5)  # Default max to 5 if missing
    if num_to_remove > 0:
        logs_to_remove = log_files[:num_to_remove]  # Get oldest logs to remove
        for log_file in logs_to_remove:
            try:
                log_file.unlink()  # Delete the log file
                deleted_logs.append(log_file.as_posix())
                # Ensure logging only runs if enabled
                if configs["logging"].get("enable", True):
                    log_utils.log_message(f'Deleted old log: {log_file.as_posix()}', category.warning.id, configs=configs)
            except Exception as e:
                if configs["logging"].get("enable", True):
                    log_utils.log_message(f'Error deleting {log_file.as_posix()}: {e}', category.error.id, configs=configs)
    return deleted_logs

def relative_path(
    filepath: str
) -> str:

    try:
        return str(Path(filepath).resolve().relative_to(project_root)).replace(".py", "")
    except ValueError:
        return filepath.replace(".py", "")  # Return original if not within project

def remove_ansi_escape_codes(
    text: str
) -> str:

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
