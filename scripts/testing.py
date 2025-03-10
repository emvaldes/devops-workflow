#!/usr/bin/env python3

# Standard library imports - Core system module
import sys

# Standard library imports - Utility modules
import json
import logging

# Standard library imports - File system-related module
from pathlib import Path

# Add the project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_variables as environment
from packages.appflow_tracer import tracing

# Import trace_utils from packages.appflow_tracer.lib.*_utils
from packages.appflow_tracer.lib import (
    log_utils
)

def main() -> None:

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    CONFIGS = tracing.setup_logging(events=["call", "return"])
    # print(f'CONFIGS: {json.dumps(CONFIGS, indent=environment.default_indent)}')

    log_utils.log_message(
        f'I am a stand-alone script minding my own business',
        environment.category.debug.id,
        configs=CONFIGS
    )

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()
