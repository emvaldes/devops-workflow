#!/usr/bin/env python3

# File: ./run.py
# Version: 0.0.8

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

def create_doc_structure(base_path, package_name):
    """Create the doc structure for the given package under the 'docs/pydoc' directory."""
    # Get the project root where the run.py script is located
    project_root = Path(__file__).resolve().parent

    # Ensure that the docs directory structure exists
    doc_dir = os.path.join(project_root, 'docs', 'pydoc', package_name)
    os.makedirs(doc_dir, exist_ok=True)
    return doc_dir

def generate_pydoc(file_path, doc_path):
    """Generate documentation for a given Python file using pydoc."""
    log_utils.log_message(
        f'Generating documentation for {file_path}...',
        environment.category.debug.id,
        configs=CONFIGS
    )

    # Convert the file path to an absolute path
    absolute_file_path = os.path.abspath(file_path)
    file_name = os.path.basename(file_path)
    doc_file_path = os.path.join(doc_path, f"{os.path.splitext(file_name)[0]}.pydoc")

    try:

        print( f'Target File: {absolute_file_path}' )
        # Run pydoc through subprocess to avoid manual parsing issues
        command = ['python', '-m', 'pydoc', absolute_file_path]
        pydoc_output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)

        # # If the file is inside a package, convert the file path into a module path
        # module_name = absolute_file_path.replace(os.getcwd() + os.sep, "").replace(os.sep, ".").replace(".py", "")
        # # Use pydoc to get the documentation for the module
        # pydoc_output = pydoc.render_doc(module_name)

        # Write the pydoc output to the .pydoc file
        with open(doc_file_path, "w", encoding="utf-8") as doc_file:
            doc_file.write(f"### Documentation for {file_path}\n\n")
            doc_file.write(f"{pydoc_output}\n")

        log_utils.log_message(
            f'Documentation saved to {doc_file_path}',
            environment.category.debug.id,
            configs=CONFIGS
        )

    except Exception as e:
    # except subprocess.CalledProcessError as e:

        # If there is an error generating pydoc, create an empty file and log the error
        log_utils.log_message(
            f'[ERROR] generating pydoc for {file_path}: {e}',
            environment.category.error.id,
            configs=CONFIGS
        )
        with open(doc_file_path, "w", encoding="utf-8") as doc_file:
            doc_file.write(f"### Documentation for {file_path}\n\n")
            doc_file.write(f"pydoc\nProblem generating pydoc: {e}\n")
        log_utils.log_message(
            f'Created an empty .pydoc file due to an error for {file_path}',
            environment.category.debug.id,
            configs=CONFIGS
        )

def scan_and_generate_docs(path_to_scan, base_doc_dir):
    """Scan the project directory and generate documentation for all Python files."""
    log_utils.log_message(
        f'Scanning project directory for Python files...',
        environment.category.debug.id,
        configs=CONFIGS
    )

    # Walk through the directory and process Python files
    for root, dirs, files in os.walk(path_to_scan):
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

    Returns:
        argparse.Namespace: The parsed arguments object containing selected options.
    """

    parser = argparse.ArgumentParser(
        description="Verify installed dependencies for compliance. "
                    "Use -f to specify a custom JSON file. Use --show-installed to display installed dependencies."
    )
    parser.add_argument(
        "-d", "--pydoc",
        action="store_true",
        help="Generate documentation for Python files."
    )
    parser.add_argument(
        "--target",
        action="store_true",
        help="Execute target Package/Module or Script"
    )
    return parser.parse_args()

def main():
    """Main function for handling user input and generating documentation."""

    # Ensure the variable exists globally
    global CONFIGS
    # CONFIGS = tracing.setup_logging(events=False)
    CONFIGS = tracing.setup_logging(events=["call", "return", "debug", "error"])
    print( f'CONFIGS: {json.dumps(CONFIGS, indent=environment.default_indent)}' )

    args = parse_arguments()
    #
    # # Parse command-line arguments
    # parser = argparse.ArgumentParser(description="Generate pydoc documentation for Python files.")
    # parser.add_argument('--pydoc', action='store_true', help="Generate documentation for Python files.")
    # parser.add_argument('--target', type=str, help="Specify the project directory to scan.")
    #
    # args = parser.parse_args()

    # Generate documentation if --pydoc flag is passed
    if args.pydoc:

        project_path = os.getcwd()  # Use current directory as the base for scanning

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
    return

if __name__ == "__main__":
    main()
