#!/usr/bin/env python3

# File: ./lib/system_variables.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system module
import sys

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Type-related module
from types import SimpleNamespace as simple

project_root = Path(__file__).resolve().parent.parent

project_logs = project_root / "logs"

project_packages = project_root / "packages"

env_filepath = project_root / ".env"

runtime_params_filename = "runtime-params.json"

runtime_params_filepath = project_root / "configs" / runtime_params_filename

system_params_filename = "system-params.json"

system_params_filepath = project_root / "configs" / system_params_filename

project_params_filename = "project-params.json"

project_params_filepath = project_root / "configs" / project_params_filename

default_params_filename = "default-params.json"

default_params_filepath = project_root / "configs" / default_params_filename

system_params_listing = [
    project_params_filepath,
    default_params_filepath
]

max_logfiles = 5

default_indent = 4

category = simple(
    calls    = simple(id="CALL",     color="\033[92m"),  # Green
    critical = simple(id="CRITICAL", color="\033[41m"),  # Red Background
    debug    = simple(id="DEBUG",    color="\033[96m"),  # Cyan
    error    = simple(id="ERROR",    color="\033[31m"),  # Bright Red
    imports  = simple(id="IMPORT",   color="\033[94m"),  # Blue
    info     = simple(id="INFO",     color="\033[97m"),  # White
    returns  = simple(id="RETURN",   color="\033[93m"),  # Yellow
    warning  = simple(id="WARNING",  color="\033[91m"),  # Red
    reset    = simple(id="RESET",    color="\033[0m")    # Reset to default
)

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])
