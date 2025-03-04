#!/usr/bin/env python3

# File: ./packages/appflow_tracer/__main__.py
# Version: 0.1.0

"""
File Path: packages/appflow_tracer/__main__.py

Description:
    AppFlow Tracing Package Entry Point

    This file serves as the execution entry point for the `appflow_tracer` package when run
    in standalone mode. It initializes the logging system and starts the tracing execution flow.

Core Features:
    - **Standalone Execution**: Allows the package to be executed directly using `python -m packages.appflow_tracer`.
    - **Logging Initialization**: Ensures structured logging is properly configured.
    - **Main Function Invocation**: Calls the `main()` function from the `tracing` module.

Usage:
    To run the `appflow_tracer` package as a standalone script:
    ```bash
    python -m packages.appflow_tracer
    ```

Dependencies:
    - tracing (for handling structured logging and execution flow)

Example:
    ```bash
    python -m packages.appflow_tracer
    ```
"""

# Package version
__version__ = "0.1.0"

from packages.appflow_tracer.tracing import main

if __name__ == "__main__":
    main()
