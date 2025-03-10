#!/usr/bin/env python3

# File: ./packages/appflow_tracer/lib/__init__.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system module
import sys

# Standard library imports - File system-related module
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import and expose key submodules
from . import (
    file_utils,
    log_utils,
    serialize_utils,
    trace_utils
)

__all__ = [
    "file_utils",
    "log_utils",
    "serialize_utils",
    "trace_utils"
]

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])
