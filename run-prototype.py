#!/usr/bin/env python3

## File: ./run.py
## Version: 0.0.2

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
import pydoc
from pathlib import Path

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
    print(f"Generating documentation for {file_path}...")

    # Convert the file path to an absolute path
    absolute_file_path = os.path.abspath(file_path)
    file_name = os.path.basename(file_path)
    doc_file_path = os.path.join(doc_path, f"{os.path.splitext(file_name)[0]}.pydoc")

    try:
        # If the file is inside a package, we need to convert the file path into a module path
        module_name = absolute_file_path.replace(os.getcwd() + os.sep, "").replace(os.sep, ".").replace(".py", "")

        # Use pydoc to get the documentation for the module
        help_output = pydoc.render_doc(module_name)

        # Write the pydoc output to the .pydoc file
        with open(doc_file_path, "w") as doc_file:
            doc_file.write(f"### Documentation for {file_path}\n\n")
            doc_file.write(f"pydoc\n{help_output}\n")

        print(f"Documentation saved to {doc_file_path}")

    except Exception as e:
        # If there is an error generating pydoc, create an empty file and log the error
        print(f"Error generating pydoc for {file_path}: {e}")
        with open(doc_file_path, "w") as doc_file:
            doc_file.write(f"### Documentation for {file_path}\n\n")
            doc_file.write(f"pydoc\nProblem generating pydoc: {e}\n")

        print(f"Created an empty .pydoc file due to an error for {file_path}")

def scan_and_generate_docs(path_to_scan, package_name):
    """Scan the project directory and generate documentation for all Python files."""
    doc_base = create_doc_structure(path_to_scan, package_name)

    # Walk through the directory and process Python files
    for root, dirs, files in os.walk(path_to_scan):
        py_files = [f for f in files if f.endswith(".py") and f not in ["__init__.py", "__main__.py"]]

        for py_file in py_files:
            file_path = os.path.join(root, py_file)
            generate_pydoc(file_path, doc_base)

def main():
    """Main function for handling user input and generating documentation."""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Generate pydoc documentation for Python files.")
    parser.add_argument('--pydoc', action='store_true', help="Generate documentation for Python files.")
    parser.add_argument('--target', type=str, help="Specify the project directory to scan.")

    args = parser.parse_args()

    # Generate documentation if --pydoc flag is passed
    if args.pydoc:

        # if not args.target:
        #     print("Error: The --target parameter must be specified with --pydoc.")
        #     sys.exit(1)
        #
        # project_path = args.target
        project_path = os.getcwd()

        if not os.path.isdir(project_path):
            print(f"Error: {project_path} is not a valid directory.")
            sys.exit(1)

        package_name = os.path.basename(project_path)

        print(f"Generating documentation for the project at {project_path}...")
        scan_and_generate_docs(project_path, package_name)
        print("Documentation generation completed successfully.")
        return

    # If --target flag is passed, execute the specified Package/Module or Script
    if args.target:
        print(f"Running package/module {args.target}...")
        subprocess.run([sys.executable, '-m', args.target])
        return

    # If no flags, print a basic message
    print("No flags provided. Use --pydoc to generate documentation or --target to run a module.")
    return

if __name__ == "__main__":
    main()
