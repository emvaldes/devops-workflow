#!/usr/bin/env python3

# File: lib/pydoc_generator.py

__package__ = "lib"
__module__ = "pydoc_generator"

__version__ = "0.1.1"  ## Package version

#-------------------------------------------------------------------------------

# Standard library imports - Core system and OS interaction modules
import os
import sys

# Standard library imports - Utility modules
import re
import subprocess

# Standard library imports - File system-related module
from pathlib import Path

# Third-party library imports - Coverage analysis
import coverage

#-------------------------------------------------------------------------------

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

#-------------------------------------------------------------------------------

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

#-------------------------------------------------------------------------------

def create_structure(
    base_path: Path,
    package_name: Path
) -> Path:

    doc_dir = base_path / package_name          ## Use Path operations
    doc_dir.mkdir(parents=True, exist_ok=True)  ## Equivalent to os.makedirs()
    return doc_dir  ## Returns a Path object

#-------------------------------------------------------------------------------

def generate_report(
    coverage_report: Path,
    configs: dict = None
):

    try:
        # Ensure the directory exists
        coverage_report.parent.mkdir(parents=True, exist_ok=True)
        # Generate the coverage summary and save it to a file
        with open(coverage_report, "w", encoding="utf-8") as summary_file:
            subprocess.run(
                ["python", "-m", "coverage", "report"],
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

#-------------------------------------------------------------------------------

def generate_coverage(
    project_path: Path,
    file_path: Path,
    base_path: Path,
    configs: dict = None
):

    # Convert to relative path
    relative_filepath = file_path.relative_to(project_path)
    # Generate coverage report for the specific file
    coverage_command = ["python", "-m", "coverage", "report", "--include", str(file_path)]
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

#-------------------------------------------------------------------------------

def generate_pydoc(
    project_path: Path,
    file_path: Path,
    docs_path: Path,
    configs: dict = None
):

    # Use Path method instead of os.path.basename()
    file_name = file_path.name
    # Use Pathlib operations
    doc_file_path = docs_path / f"{file_path.stem}.pydoc"
    # Ensure the file path is relative to the project root
    relative_filepath = Path(file_path).relative_to(project_path)
    log_utils.log_message(
        f'\n[REVIEW] Generating documentation: {str(relative_filepath)} ...',
        environment.category.calls.id,
        configs=configs
    )
    # Convert the path into a proper module name by joining parts with "."
    ## Fixes 'lib.pydoc_generator'
    module_name = ".".join( relative_filepath.with_suffix("").parts )
    ## Updated logic for script detection
    is_script = any('.' in part for part in relative_filepath.parts[:-1])
    ## Processing as either a script or module
    pydoc_command = [
        'python', '-m', 'pydoc',
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

#-------------------------------------------------------------------------------

def create_pydocs(
    project_path: Path,
    base_path: Path,
    files_list: list[Path],
    configs: dict = None
):

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

#-------------------------------------------------------------------------------

def main() -> None:
    pass

#-------------------------------------------------------------------------------

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
