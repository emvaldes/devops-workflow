#!/usr/bin/env python3

# File: ./lib/__init__.py
__version__ = "0.1.0"  ## Package version

import sys
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])
