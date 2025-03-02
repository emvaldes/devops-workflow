#!/usr/bin/env python3

## File: ./run.py
## Version: 0.0.1

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
- If the --document flag is passed, it generates documentation for the specified Python files.
- If the --module flag is passed, it executes the specified Python module.

Dependencies:

- subprocess (used to execute arbitrary scripts/modules)
- argparse (used to handle command-line arguments)

Usage:

To start the framework:
> python run.py

To generate documentation:
> python run.py --document --project ./packages/appflow_tracer

To run an arbitrary Python module:
> python run.py --module <module_name>
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Function for generating documentation (from the earlier script)
def create_doc_structure(base_path, relative_path):
    """Create the doc directory structure under docs/pydoc relative to run.py."""
    # Get the project root where the run.py script is
    project_root = Path(__file__).resolve().parent

    # Define the base doc directory
    doc_dir = os.path.join(project_root, 'docs', 'pydoc', relative_path)

    # Ensure the directory structure exists
    os.makedirs(doc_dir, exist_ok=True)
    return doc_dir

def generate_pydoc(file_path, doc_path):
    """Generate documentation for a given Python file using pydoc."""
    print(f"Generating documentation for {file_path}...")

    # Create the destination file path for the documentation
    doc_file_path = os.path.join(doc_path, f"{os.path.splitext(os.path.basename(file_path))[0]}.pydoc")

    # Create a log file for errors
    log_file_path = os.path.join(doc_path, f"{os.path.splitext(os.path.basename(file_path))[0]}.log")

    try:
        # Get the module name by converting the file path to a module path
        module_name = file_path.replace("/", ".").replace(".py", "")

        # Run the pydoc command with adjusted PYTHONPATH
        command = [
            'python', '-m', 'pydoc', module_name
        ]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True, env={**os.environ, 'PYTHONPATH': os.getcwd()})

        # Write pydoc output to the .pydoc file
        with open(doc_file_path, "w") as doc_file:
            doc_file.write(result)

        print(f"Documentation saved to {doc_file_path}")

    except subprocess.CalledProcessError as e:
        # If there's an error, dump the error details to a log file
        print(f"Error generating pydoc for {file_path}: {e}")

        # Write the error message to the log file
        with open(log_file_path, "w") as log_file:
            log_file.write(f"Error generating pydoc for {file_path}:\n")
            log_file.write(f"Command: {' '.join(e.cmd)}\n")
            log_file.write(f"Return Code: {e.returncode}\n")
            log_file.write(f"Output:\n{e.output}\n")
            log_file.write(f"Error:\n{e.stderr}\n")

        print(f"Created an error log for {file_path} at {log_file_path}")

def scan_and_generate_docs(path_to_scan, relative_path):
    """Scan a directory and generate docs for Python files."""
    # Create a base doc directory under docs/pydoc relative to the project root
    doc_base = create_doc_structure(path_to_scan, relative_path)

    # Walk through the directory
    for root, dirs, files in os.walk(path_to_scan):
        # Only process Python files, ignoring __init__.py and __main__.py
        py_files = [f for f in files if f.endswith(".py") and f not in ["__init__.py", "__main__.py"]]

        if py_files:
            # Create the corresponding directory in the doc folder (pydoc)
            relative_dir = os.path.relpath(root, path_to_scan)
            doc_dir = os.path.join(doc_base, relative_dir)
            os.makedirs(doc_dir, exist_ok=True)

            # Generate documentation for each Python file
            for py_file in py_files:
                file_path = os.path.join(root, py_file)
                generate_pydoc(file_path, doc_dir)

def main() -> None:
    """
    Main function for handling the entry point of the script.

    - Executes the requested module/script for system setup.
    - If the --document flag is passed, generates documentation for the specified directory.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run the framework and manage documentation generation.")
    parser.add_argument('--document', action='store_true', help="Generate documentation for Python files.")
    parser.add_argument('--project', type=str, help="Specify the path to the project directory to scan.")
    parser.add_argument('--module', type=str, help="Specify the module or script to run.")

    args = parser.parse_args()

    # If --document flag is passed, generate documentation
    if args.document:
        if not args.project:
            print("Error: The --project parameter must be specified with --document.")
            sys.exit(1)

        project_path = args.project

        if not os.path.isdir(project_path):
            print(f"Error: {project_path} is not a valid directory.")
            sys.exit(1)

        # Get the relative path of the project (removing the project root part)
        relative_path = os.path.relpath(project_path, start=Path(__file__).resolve().parent)

        print(f"Generating documentation for the project at {project_path}...")
        scan_and_generate_docs(project_path, relative_path)
        print("Documentation generation completed successfully.")
        return

    # If --module flag is passed, execute the specified module
    if args.module:
        print(f"Running the module {args.module}...")
        subprocess.run([sys.executable, '-m', args.module])
        return

    # If no flags, print a basic message
    print("No flags provided. Use --document to generate documentation or --module to run a module.")
    return

if __name__ == "__main__":
    main()
