#!/usr/bin/env python3

# File: ./run.py
__version__ = "0.1.0"  ## Package version

"""
File: ./run.py

Description:
    Framework Execution Entry Point

    This script serves as the main launcher for the framework, ensuring proper initialization,
    system validation, and execution of requested operations. It can generate documentation
    for Python scripts and execute arbitrary Python modules.

Core Features:
    - **System Validation & Setup**: Ensures the framework environment is correctly configured.
    - **Python Documentation Generation**: Uses `pydoc` to generate structured documentation.
    - **Module Execution**: Provides the ability to run specified Python modules or scripts.
    - **Dynamic File Collection**: Recursively scans the project for non-empty Python files.
    - **Logging & Debugging**: Captures execution details and potential errors.

Features:
    - Executes the requested module/script to perform system validation and setup.
    - Ensures all required dependencies and configurations are initialized.
    - Provides a single-command entry point for launching the framework.
    - Integrates functionality for generating documentation for Python and YAML files in a specific path.
    - Allows running an arbitrary Python module.

Expected Behavior:


Usage:
    To launch the framework:
    ```bash
    python run.py
    ```

    To generate Python documentation:
    ```bash
    python run.py --pydoc
    ```

    To generate YAML documentation:
    ```bash
    python run.py --yamldoc
    ```

    To run an arbitrary module:
    ```bash
    python run.py --target <module_name>
    ```

Dependencies:
    - os
    - sys
    - json
    - re
    - argparse (used to handle command-line arguments)
    - subprocess (used to execute arbitrary scripts/modules)
    - pathlib
    - system_variables (for project environment settings)
    - log_utils (for structured logging)
    - pydoc_generator (for documentation generation)
    - yaml_doc_generator (for YAML documentation extraction)

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to incorrect parameters, invalid paths, or execution errors.
"""

import os
import sys

import subprocess
import argparse

import re
import json

import pydoc
import pytest

import logging

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

# # Setup logging configuration
# logging.basicConfig(level=logging.INFO)

from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

from lib import system_variables as environment
from lib import pydoc_generator as pydoc_engine

# from lib import yaml_doc_generator as yamldoc_engine

def collect_files(
    target_dir: str,
    extensions: list[str]
) -> list[str]:
    """
    Recursively scans a directory for non-empty files matching the specified extensions.

    This function ensures that only files with actual content are collected, preventing
    the processing of empty or irrelevant files.

    Args:
        target_dir (str): The directory to scan.
        extensions (List[str]): A list of file extensions to filter.

    Returns:
        List[str]: A list of absolute file paths that match the specified extensions.

    Raises:
        ValueError: If the provided target directory does not exist.

    Example:
        ```python
        python_files = collect_files("/project/src", [".py"])
        ```
    """

    target_path = Path(target_dir).resolve()

    if not target_path.is_dir():
        raise ValueError(f"Error: {target_dir} is not a valid directory.")

    # Collect only non-empty matching files
    files = [
        str(file.resolve())
        for ext in extensions
        for file in target_path.rglob(f"*{ext}")
        if file.stat().st_size > 0  # Ensure file is not empty
    ]

    return files

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for framework execution.

    This function processes command-line flags that determine the execution behavior of
    the framework, such as generating documentation or executing a target module.

    Returns:
        argparse.Namespace: The parsed arguments object containing selected options.

    Example:
        ```bash
        python run.py --pydoc
        python run.py --yamldoc
        python run.py --target my_module
        ```
    """

    parser = argparse.ArgumentParser(
        description="Verify installed dependencies for compliance. "
                    "Use -d/--pydoc to generate documentation."
                    "Use -y/--yamldoc to generate YAML documentation. "
                    "Use -t/--target to execute a module."
    )
    parser.add_argument(
        "-d", "--pydoc",
        action="store_true",
        help="Generate documentation for Python files."
    )
    parser.add_argument(
        "-y", "--yamldoc",
        action="store_true",
        help="Generate documentation for YAML files."
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        help="Execute target Package/Module or Script"
    )
    return parser.parse_args()

def main():
    """
    Framework Entry Point.

    This function orchestrates the execution of the framework based on the provided command-line
    arguments. It handles:
    - Generating Python documentation via `pydoc` if the `--pydoc` flag is passed.
    - Running a specified Python module if the `--target` flag is provided.
    - Logging execution details and error handling.

    Returns:
        None: Executes the requested functionality and exits accordingly.

    Behavior:
        - If `--pydoc` is passed, the script generates documentation for Python files.
        - If `--target <module>` is passed, it attempts to execute the specified module.
        - If no flags are provided, it logs a usage message.

    Example:
        ```bash
        python run.py --pydoc
        python run.py --yamldoc
        python run.py --target some_module
        ```
    """

    # Ensure the variable exists globally
    global CONFIGS

    # CONFIGS = tracing.setup_logging(events=False)
    CONFIGS = tracing.setup_logging(events=["call", "return", "debug", "error"])
    print(
        f'CONFIGS: {json.dumps(
            CONFIGS, indent=environment.default_indent
        )}'
    )

    args = parse_arguments()

    ## Use current directory as the base for scanning
    # project_path = os.getcwd()
    project_path = environment.project_root

    if not os.path.isdir(project_path):
        log_utils.log_message(
            f'Error: {project_path} is not a valid directory.',
            environment.category.error.id,
            configs=CONFIGS
        )
        sys.exit(1)

    # Base documentation folder should be 'docs/pydoc'
    base_path = os.path.join(
        project_path,
        'docs',
        'pydoc'
    )

    log_utils.log_message(
        f'Generating project documentation at: {project_path}',
        environment.category.debug.id,
        configs=CONFIGS
    )

    # Generate documentation if --pydoc flag is passed
    if args.pydoc:

        file_extensions = [".py"]  ## Defined by CLI flag
        files_list = collect_files(
            project_path,
            file_extensions
        )

        pydoc_engine.create_pydocs(
            project_path=project_path,
            base_path=base_path,
            files_list=files_list,
            configs=CONFIGS
        )

        log_utils.log_message(
            f'Documentation generation completed successfully.',
            environment.category.debug.id,
            configs=CONFIGS
        )

    if args.yamldoc:

        files_list = collect_files(
            project_path,
            [".yaml", ".yml"]
        )

        yamldoc_engine.create_yamldocs(
            project_path=project_path,
            base_path=Path(project_path) / "docs/yamldoc",
            files_list=files_list,
            configs=CONFIGS
        )

    # If --target flag is passed, execute the specified Package/Module or Script
    if args.target:

        log_utils.log_message(
            f'Running Package/Module {args.target}...',
            environment.category.debug.id,
            configs=CONFIGS
        )
        subprocess.run([sys.executable, '-m', args.target])
        return

    # If no flags, print a basic message
    log_utils.log_message(
        f'No flags provided. Use --pydoc to generate documentation or --target to run a Package/Module or Script.',
        environment.category.debug.id,
        configs=CONFIGS
    )

if __name__ == "__main__":
    main()
