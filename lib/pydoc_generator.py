#!/usr/bin/env python3

# File: lib/pydoc_generator.py
__version__ = "0.1.1"  ## Package version

"""
File: lib/pydoc_generator.py

Description:
    Automated Python Documentation Generator (PyDoc)

    This module provides a framework for generating documentation for Python scripts and packages
    within a project using the `pydoc` module. It ensures that documentation is structured correctly
    and saved in an organized manner.

Core Features:
    - **Dynamic Documentation Generation**: Automates the process of generating PyDoc documentation.
    - **Path Handling**: Uses `pathlib` for robust and cross-platform path operations.
    - **Error Handling & Logging**: Captures errors and logs messages for debugging.
    - **Flexible Execution**: Distinguishes between modules and standalone scripts for correct PyDoc execution.
    - **Output Sanitization**: Redacts sensitive system paths from generated documentation.
    - **Coverage Integration**: Generates separate `.coverage` files per module.

Usage:
    To generate PyDoc documentation for all Python files in a project:
    ```bash
    python run.py --pydoc
    ```

Dependencies:
    - os
    - sys
    - re
    - subprocess
    - pathlib
    - system_variables (for project environment settings)
    - log_utils (for structured logging)
    - coverage (for tracking execution coverage)

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to incorrect file paths or PyDoc errors.

Example:
    ```bash
    python -m pydoc lib.pydoc_generator
    ```
"""

import sys
import os

import coverage
import re
import subprocess

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

def create_structure(
    base_path: Path,
    package_name: Path
) -> Path:
    """
    Create the directory structure for storing PyDoc-generated documentation.

    This function ensures that the necessary directory structure exists under the
    `docs/pydoc` directory to store documentation files. It will create the directories
    if they do not already exist.

    Args:
        base_path (Path): The base path where documentation will be stored.
        package_name (Path): The relative package path that determines the storage directory.

    Returns:
        Path: The absolute path to the created documentation directory.

    Notes:
        - Uses `mkdir(parents=True, exist_ok=True)` to ensure all parent directories exist.
        - Accepts `Path` objects for improved cross-platform compatibility.
    """

    doc_dir = base_path / package_name          ## Use Path operations
    doc_dir.mkdir(parents=True, exist_ok=True)  ## Equivalent to os.makedirs()

    return doc_dir  ## Returns a Path object

def generate_report(
    coverage_report: Path,
    configs: dict = None
):
    """
    Generates and saves a textual summary of test coverage.

    Args:
        coverage_report (Path): The output file where the summary will be stored.
        configs (dict, optional): Logging configurations.

    Behavior:
        - Runs `coverage report` to generate a textual coverage summary.
        - Saves the output to `coverage_report`.
        - If no coverage data is found, logs a warning.

    Raises:
        CalledProcessError: If the `coverage report` command fails unexpectedly.
    """

    try:
        # Ensure the directory exists
        coverage_report.parent.mkdir(parents=True, exist_ok=True)
        # Generate the coverage summary and save it to a file
        with open(coverage_report, "w", encoding="utf-8") as summary_file:
            subprocess.run(
                [
                    "python",
                    "-m",
                    "coverage",
                    "report"
                ],
                stdout=summary_file,  # Redirect output to file
                stderr=subprocess.PIPE,  # Capture any errors
                text=True,
                check=True
            )
        # Confirm if the report file has content
        if coverage_report.stat().st_size == 0:
            log_utils.log_message(
                f'[WARNING] Generated Coverage Report is empty.',
                environment.category.warning.id,
                configs=configs
            )
    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'[ERROR] Failed to generate coverage summary: {e}',
            environment.category.error.id,
            configs=configs
        )

def generate_coverage(
    project_path: Path,
    file_path: Path,
    base_path: Path,
    configs: dict = None
):
    """
    Generate and save coverage data to a structured directory.

    Args:
        project_path (Path): The root path of the project.
        file_path (Path): The Python file for which coverage is generated.
        base_path (Path): The base directory where coverage files are stored.
        configs (dict, optional): Additional configuration parameters for logging.
    """

    # Convert to relative path
    relative_filepath = file_path.relative_to(project_path)

    # Generate coverage report for the specific file
    coverage_command = [
        "python",
        "-m",
        "coverage",
        "report",
        "--include",
        str(file_path)
    ]

    try:
        coverage_output = subprocess.check_output(
            coverage_command,
            stderr=subprocess.STDOUT,
            text=True
        )

    except subprocess.CalledProcessError as e:
        if "No data to report." in e.output:
            log_utils.log_message(
                f'[COVERAGE] No coverage data available: "{relative_filepath}". Skipping coverage report.',
                environment.category.error.id,
                configs=configs
            )
            return  # No need to save empty coverage files
        else:
            raise

    # Create the coverage storage structure once
    coverage_path = create_structure(base_path, relative_filepath.parent)

    # Construct full path for the coverage file
    coverage_file_path = coverage_path / f"{file_path.stem}.coverage"

    # Save coverage if data exists
    with open(coverage_file_path, "w", encoding="utf-8") as coverage_file:
        coverage_file.write(coverage_output)

    log_utils.log_message(
        f'[COVERAGE] Coverage saved to: {coverage_file_path.relative_to(project_path)}',
        environment.category.info.id,
        configs=configs
    )

def generate_pydoc(
    project_path: Path,
    file_path: Path,
    docs_path: Path,
    configs: dict = None
):
    """
    Generate and store PyDoc documentation for a given Python file.

    This function invokes `pydoc` to generate documentation for a Python script or module
    and saves the output in the designated documentation directory. Additionally, it appends
    the test coverage report for the processed file.

    Args:
        project_path (Path): The root path of the project.
        file_path (Path): The Python file for which documentation will be generated.
        docs_path (Path): The directory where the generated documentation will be stored.
        configs (dict, optional): Additional configuration parameters for logging.

    Returns:
        None: This function does not return any value but writes documentation or error messages to disk.

    Behavior:
        - Differentiates between scripts and modules to invoke `pydoc` correctly.
        - Stores the generated documentation in `docs/pydoc/<module>.pydoc`.
        - Sanitizes system paths in the output to avoid exposing absolute paths.

    Example:
        ```python
        generate_pydoc(
            Path("<project-location>"),
            Path("<project-location>/src/module.py"),
            Path("<project-location>/docs/pydoc")
        )
        ```
    """

    file_name = file_path.name  ## Use Path method instead of os.path.basename()
    doc_file_path = docs_path / f"{file_path.stem}.pydoc"  ## Use Pathlib operations

    # Ensure the file path is relative to the project root
    relative_filepath = Path(file_path).relative_to(project_path)      ## Ensure it's relative

    log_utils.log_message(
        f'\n[REVIEW] Generating documentation: {str(relative_filepath)} ...',
        environment.category.calls.id,
        configs=configs
    )

    # Convert the path into a proper module name by joining parts with "."
    module_name = ".".join( relative_filepath.with_suffix("").parts )  ## Fixes 'lib.pydoc_generator'

    ## Updated logic for script detection
    is_script = any('.' in part for part in relative_filepath.parts[:-1])

    ## Processing as either a script or module
    pydoc_command = [
        'python',
        '-m',
        'pydoc',
        f'./{relative_filepath}' if is_script else module_name
    ]

    # log_utils.log_message(
    #     f'[INFO] Relative File Path: {relative_filepath}',
    #     environment.category.info.id,
    #     configs=configs
    # )
    # log_utils.log_message(
    #     f'[INFO] Converted Module Name: {module_name}',
    #     environment.category.info.id,
    #     configs=configs
    # )
    log_utils.log_message(
        f'[ACTION] PyDoc Command: {" ".join(pydoc_command)}',
        environment.category.debug.id,
        configs=configs
    )

    try:

        ## Run pydoc pydoc_command and capture output
        pydoc_output = subprocess.check_output(
            pydoc_command,
            stderr=subprocess.STDOUT,
            text=True
        )

        generate_coverage(
            project_path,
            file_path,
            base_path=Path(project_path) / "docs" / "coverage",
            configs=configs
        )

        # Perform both sanitizations in one step using regex
        sanitized_output = re.sub(
            rf'({re.escape(str( project_path ))}|{re.escape(str( Path.home() ))})',
            lambda match: "<project-location>" if match.group(0) == str( project_path ) else "<user-home>",
            pydoc_output
        )

        ## Write successful documentation output
        with open(doc_file_path, "w", encoding="utf-8") as doc_file:
            doc_file.write(f"### Documentation for {relative_filepath}\n\n")
            doc_file.write(f"{sanitized_output}\n")

        relative_doc_path = (
            doc_file_path.relative_to(project_path)
            if project_path in doc_file_path.parents
            else doc_file_path
        )
        log_utils.log_message(
            f'[PYDOC] Documentation saved to: {relative_doc_path}',
            environment.category.debug.id,
            configs=configs
        )

    except subprocess.CalledProcessError as e:
        ## Handle pydoc failures properly
        log_utils.log_message(
            f'[ERROR] Generating PyDoc: {file_path}: {e}',
            environment.category.error.id,
            configs=configs
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
                    configs=configs
                )
            else:
                log_utils.log_message(
                    f'[WARNING] Skipping rename: {doc_file_path} does not exist, logging error message instead.',
                    environment.category.warning.id,
                    configs=configs
                )
        except Exception as rename_error:
            ## If there is an error generating pydoc, create an empty file and log the error
            log_utils.log_message(
                f'[ERROR] Failed to rename "{doc_file_path}" to "{error_file_path}": {rename_error}',
                environment.category.error.id,
                configs=configs
            )

        ## Write error message to the error file
        with open(error_file_path, "a", encoding="utf-8") as error_file:
            error_file.write(f"PyDoc Error:\n{e}\n")

        log_utils.log_message(
            f'Updated {error_file_path} with error details',
            environment.category.debug.id,
            configs=configs
        )

    finally:
        log_utils.log_message(
            f'[COMPLETE] Finished processing: {relative_filepath}',
            environment.category.returns.id,
            configs=configs
        )

def create_pydocs(
    project_path: Path,
    base_path: Path,
    files_list: list[Path],
    configs: dict = None
):
    """
    Process multiple Python files and generate PyDoc documentation.

    This function iterates through a list of Python files, generates their documentation,
    and stores them in a structured format inside `docs/pydoc`.

    Args:
        project_path (Path): The root directory of the project.
        base_path (Path): The base directory where documentation will be stored.
        files_list (list[Path]): A list of Python file paths to document.
        configs (dict, optional): Configuration settings for logging.

    Returns:
        None: Documentation files are generated and stored in the appropriate directories.

    Example:
        ```python
        create_pydocs(
            Path("<project-location>"),
            Path("<project-location>/docs/pydoc"),
            [Path("<project-location>/src/module1.py"), Path("<project-location>/src/module2.py")]
        )
        ```
    """

    log_utils.log_message(
        f'[INFO] Processing Python files:\n{"\n".join(
            f"  - {os.path.relpath(file, project_path)}" for file in files_list
        )}',
        environment.category.info.id,
        configs=configs
    )

    try:

        for file_path in files_list:
            ## Ensure `file_path` is a Path object
            file_path = Path(file_path).resolve()

            ## Convert to a relative path from the project root
            relative_dir = file_path.parent.relative_to( Path( project_path ) )

            ## Create the directory for the pydoc files
            docs_path = create_structure(
                base_path=Path(base_path),
                package_name=str(relative_dir)
            )

            generate_pydoc(
                project_path,
                file_path,
                docs_path,
                configs=configs
            )

    except subprocess.CalledProcessError as e:
        log_utils.log_message(
            f'[ERROR] generating pydocs for {project_path}: {e}',
            environment.category.error.id,
            configs=configs
        )
