#!/usr/bin/env python3

# File: ./run.py
# Version: 0.0.9

"""
File Path: ./run.py

Description:

Main Execution Entry Point for the Framework

This script acts as the launcher for the framework, ensuring that system configurations,
dependencies, and user privileges are validated before execution.

Features:

- Executes the requested module/script to perform system validation and setup.
- Ensures all required dependencies and configurations are initialized.
- Provides a single-command entry point for launching the framework.
- Integrates functionality for generating documentation for Python files in a specific path.
- Allows running an arbitrary Python module.

Expected Behavior:

- This script **must be run from the project root**.
- Any errors encountered in the execution will be printed to the console.
- The script automatically terminates if critical dependencies are missing.
- If the --pydoc flag is passed, it generates documentation for the specified Python files.
- If the --target flag is passed, it executes the specified Python module.

Dependencies:

- subprocess (used to execute arbitrary scripts/modules)
- argparse (used to handle command-line arguments)

Usage:

To start the framework:
> python run.py

To generate documentation:
> python run.py --pydoc

To run an arbitrary Python Package/Module/Script:
> python run.py --target <module_name>
"""

import os
import sys

import subprocess
import argparse
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

def create_doc_structure(
    base_path,
    package_name
):
    """
    Create the doc structure for the given package under the 'docs/pydoc' directory.

    This function ensures that the necessary directory structure for the documentation is created,
    specifically within the `docs/pydoc` directory.

    Args:
        base_path (str): The base path where the documentation will be created.
        package_name (str): The name of the package for which the documentation is being created.

    Returns:
        str: The path to the created documentation directory.
    """

    # Get the project root where the run.py script is located
    project_root = Path(__file__).resolve().parent

    # Ensure that the docs directory structure exists
    doc_dir = os.path.join(project_root, 'docs', 'pydoc', package_name)
    os.makedirs(doc_dir, exist_ok=True)
    return doc_dir

def generate_pydoc(
    file_path,
    doc_path
):
    """
    Generate documentation for a given Python file using pydoc.

    This function invokes the `pydoc` module to generate documentation for a Python file
    and stores it in the specified documentation directory. If the generation fails, an error file is created.

    Args:
        file_path (str): The path to the Python file for which documentation will be generated.
        doc_path (str): The directory where the generated documentation will be saved.

    Returns:
        None: This function does not return any value but generates documentation or handles errors.
    """

    project_root = Path(__file__).resolve().parent

    log_utils.log_message(
        f'Generating documentation for {file_path}...',
        environment.category.debug.id,
        configs=CONFIGS
    )

    # Convert file path to relative project path
    relative_file_path = os.path.relpath(file_path, start=project_root)
    log_utils.log_message(
        f'Relative File Path: {relative_file_path}',
        environment.category.debug.id,
        configs=CONFIGS
    )

    file_name = os.path.basename(file_path)
    doc_file_path = os.path.join(doc_path, f"{os.path.splitext(file_name)[0]}.pydoc")

    # Determine correct command based on directory structure
    if any(part.startswith('.') for part in Path(relative_file_path).parts):
        # If any folder in the path starts with '.', treat it as a script
        command = ['python', '-m', 'pydoc', f'./{relative_file_path}']
    else:
        # Otherwise, treat it as a module
        module_name = relative_file_path.replace(os.sep, ".").replace(".py", "")
        command = ['python', '-m', 'pydoc', module_name]

    log_utils.log_message(
        f'Running PyDoc Command: {" ".join(command)}',
        environment.category.debug.id,
        configs=CONFIGS
    )

    try:
        # Run pydoc command and capture output
        pydoc_output = subprocess.check_output(
            command, stderr=subprocess.STDOUT,
            text=True
        )

        # Write successful documentation output
        with open(doc_file_path, "w", encoding="utf-8") as doc_file:
            doc_file.write(f"### Documentation for {file_path}\n\n")
            doc_file.write(f"{pydoc_output}\n")

        log_utils.log_message(
            f'Documentation saved to {doc_file_path}',
            environment.category.debug.id,
            configs=CONFIGS
        )

    except subprocess.CalledProcessError as e:
        # Handle pydoc failures properly
        log_utils.log_message(
            f'[ERROR] generating pydoc for {file_path}: {e}',
            environment.category.error.id,
            configs=CONFIGS
        )

        ## Split the file path into name and extension
        # file_root, _ = os.path.splitext(file_path)
        error_file_path = f'{doc_file_path}.error'

        try:
            if os.path.exists(doc_file_path):
                os.rename(doc_file_path, error_file_path)
                log_utils.log_message(
                    f'Renamed {doc_file_path} to {error_file_path} due to an error',
                    environment.category.debug.id,
                    configs=CONFIGS
                )
            else:
                log_utils.log_message(
                    f'[WARNING] Skipping rename: {doc_file_path} does not exist, logging error message instead.',
                    environment.category.warning.id,
                    configs=CONFIGS
                )
        except Exception as rename_error:
            ## If there is an error generating pydoc, create an empty file and log the error
            log_utils.log_message(
                f'[ERROR] Failed to rename {doc_file_path} to {error_file_path}: {rename_error}',
                environment.category.error.id,
                configs=CONFIGS
            )

        # Write error message to the error file
        with open(error_file_path, "a", encoding="utf-8") as error_file:
            error_file.write(f"PyDoc Error:\n{e}\n")

        log_utils.log_message(
            f'Updated {error_file_path} with error details',
            environment.category.debug.id,
            configs=CONFIGS
        )

    finally:
        log_utils.log_message(
            f'Finished processing {file_path}',
            environment.category.debug.id,
            configs=CONFIGS
        )

def scan_and_generate_docs(
    path_to_scan,
    base_doc_dir
):
    """
    Scan the project directory and generate documentation for all Python files.

    This function walks through the project directory, scanning for all Python files,
    excluding `__init__.py` and `__main__.py`, and generates documentation for each file.

    Args:
        path_to_scan (str): The base directory to scan for Python files.
        base_doc_dir (str): The base directory where the documentation will be saved.

    Returns:
        None: This function does not return any value but generates documentation for each Python file found.
    """

    log_utils.log_message(
        f'Scanning project directory for Python files...',
        environment.category.debug.id,
        configs=CONFIGS
    )

    # Walk through the directory and process Python files
    for root, _, files in os.walk(path_to_scan):
        py_files = [f for f in files if f.endswith(".py") and f not in ["__init__.py", "__main__.py"]]

        for py_file in py_files:
            # Construct relative path for the module, which will be used for the doc structure
            relative_dir = os.path.relpath(root, path_to_scan)

            # Create the directory for the pydoc files
            doc_dir = create_doc_structure(base_doc_dir, relative_dir)

            file_path = os.path.join(root, py_file)
            generate_pydoc(file_path, doc_dir)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for specifying the requirements file
    and displaying the installed dependencies.

    Args:
        None

    Returns:
        argparse.Namespace: The parsed arguments object containing selected options.
    """

    parser = argparse.ArgumentParser(
        description="Verify installed dependencies for compliance. "
                    "Use -d/--pydoc to generate documentation. Use -t/--target to execute a module."
    )
    parser.add_argument(
        "-d", "--pydoc",
        action="store_true",
        help="Generate documentation for Python files."
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        help="Execute target Package/Module or Script"
    )
    return parser.parse_args()

def main():
    """
    Main function for handling user input and generating documentation.

    This function processes command-line arguments, generates documentation if requested,
    or runs a specified Python module based on user input. It handles the configuration,
    sets up logging, and invokes the appropriate functions based on the flags provided.

    Args:
        None

    Returns:
        None: This function does not return any value but performs the required actions based on user input.
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

    # Generate documentation if --pydoc flag is passed
    if args.pydoc:
        # Use current directory as the base for scanning
        project_path = os.getcwd()

        if not os.path.isdir(project_path):
            log_utils.log_message(
                f'Error: {project_path} is not a valid directory.',
                environment.category.error.id,
                configs=CONFIGS
            )
            sys.exit(1)

        # Base documentation folder should be 'docs/pydoc'
        base_doc_dir = os.path.join(project_path, 'docs', 'pydoc')

        log_utils.log_message(
            f'Generating documentation for the project at {project_path}...',
            environment.category.debug.id,
            configs=CONFIGS
        )
        scan_and_generate_docs(project_path, base_doc_dir)
        log_utils.log_message(
            f'Documentation generation completed successfully.',
            environment.category.debug.id,
            configs=CONFIGS
        )
        return

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
