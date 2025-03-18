#!/usr/bin/env python3

# File: ./packages/appflow_tracer/__init__.py

__package__ = "packages.applfow_tracer"
__module__ = "__init__"

__version__ = "0.1.0"  ## Package version

#-------------------------------------------------------------------------------

# Standard library imports - Core system module
import sys

# Standard library imports - File system-related module
from pathlib import Path

#-------------------------------------------------------------------------------

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

#-------------------------------------------------------------------------------

# from .tracing import (
from packages.appflow_tracer.tracing import (
    setup_logging
)
# from .lib import (
from packages.appflow_tracer.lib import (
    file_utils,
    log_utils,
    serialize_utils,
    trace_utils
)

#-------------------------------------------------------------------------------

# Explicitly define available functions
__all__ = [
    "setup_logging",
    "file_utils",
    "log_utils",
    "serialize_utils",
    "trace_utils"
]

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])
