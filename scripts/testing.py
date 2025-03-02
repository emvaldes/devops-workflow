#!/usr/bin/env python3

"""
File Path: ./scripts/testing.py

Description:

Standalone Testing Script for Framework Logging

This script serves as a test module to verify logging and tracing capabilities.
It initializes structured logging via `packages.appflow_tracer.tracing`,
prints configuration details, and runs a simple test output.

Features:

- Configures logging using `tracing.setup_logging()`.
- Prints the loaded logging configuration in JSON format.
- Serves as a standalone script that can be run independently.

Expected Behavior:

- The script prints the structured logging configuration.
- Demonstrates logging setup and verification for debugging purposes.
- Can be used as a simple test script for logging functionality.

Dependencies:

- `packages.appflow_tracer.tracing` (for structured logging)
- `sys`, `json`, `logging`, `pathlib` (for system interaction and logging setup)

Usage:

To execute the test:
> python scripts/testing.py
"""

import sys
import json
import logging

from pathlib import Path

# Add the project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib import system_variables as environment
from packages.appflow_tracer import tracing

# Import trace_utils from packages.appflow_tracer.lib.*_utils
from packages.appflow_tracer.lib import (
    log_utils
)

def main() -> None:
    """
    Execute a standalone test to verify the structured logging system.

    This function:
    - Configures logging using `tracing.setup_logging()`.
    - Prints the loaded logging configuration in JSON format.
    - Displays a test output message.

    Expected Behavior:
    - The script prints structured logging configuration details.
    - Demonstrates the integration of logging setup in a simple, standalone script.

    Raises:
        Exception: If an error occurs during logging setup.

    Returns:
        None

    Example:
        >>> python scripts/testing.py
        CONFIGS: {
            "logging": { ... }
        }
        I am a stand-alone script minding my own business.
    """

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    CONFIGS = tracing.setup_logging(events=["call", "return"])
    # print(f'CONFIGS: {json.dumps(CONFIGS, indent=environment.default_indent)}')

    log_utils.log_message(
        f'I am a stand-alone script minding my own business',
        environment.category.debug.id,
        configs=CONFIGS
    )

if __name__ == "__main__":
    main()
