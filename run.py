#!/usr/bin/env python3

# File: ./run.py

__module__ = "run"
__version__ = "0.1.0"  # Module version

# Standard library imports - Core system and OS interaction modules
import os
import sys
import subprocess

# Standard library imports - Utility modules
import argparse
import json
import logging
import pydoc
import re

# Standard library imports - File system-related module
from pathlib import Path

# Third-party library imports - Testing and coverage tools
import coverage
import pytest

## Define base directories
LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

## Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

## Setup logging configuration
# logging.basicConfig(level=logging.INFO)

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import pydoc_generator as pydoc_engine
from lib import system_variables as environment
from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import log_utils

def collect_files(
    target_dir: str,
    extensions: list[str],
    ignore_list: list[str] = None
) -> list[str]:

    target_path = Path(target_dir).resolve()
    if not target_path.is_dir():
        raise ValueError(f"Error: {target_dir} is not a valid directory.")

    ignore_set = set(ignore_list) if ignore_list else set()  # ✅ Convert to set for faster lookups

    # ✅ Collect only non-empty matching files
    files = [
        str(file.resolve())
        for ext in extensions
        for file in target_path.rglob(f"*{ext}")
        if file.stat().st_size > 0  # ✅ Ensure file is not empty
        and not any(file.match(pattern) for pattern in ignore_set)  # ✅ Ignore files in `ignore_list`
    ]
    return files

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Verify installed dependencies for compliance. "
                    "Use -d/--pydoc to generate documentation."
                    "Use -c/--coverage to enable test coverage tracking."
                    "Use -t/--target to execute a module."
    )
    parser.add_argument(
        "-d", "--pydoc",
        action="store_true",
        help="Generate documentation for Python files."
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Enable PyTest and Coverage tracking."
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        help="Execute target Package/Module or Script"
    )
    return parser.parse_args()

def main():

    # Ensure the variable exists globally
    global CONFIGS
    # CONFIGS = tracing.setup_logging(events=False)
    CONFIGS = tracing.setup_logging(events=["call", "return"])
    # print(
    #     f'CONFIGS: {json.dumps(
    #         CONFIGS, indent=environment.default_indent
    #     )}'
    # )
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
    ## If coverage flag is set, enable coverage tracking
    cov = None
    if args.coverage:
        os.environ["COVERAGE_PROCESS_START"] = str(Path(".coveragerc").resolve())
        cov = coverage.Coverage(branch=True, source=["packages", "lib"])
        cov.start()
        log_utils.log_message(
            f'\n[ACTION] Coverage tracking enabled.',
            environment.category.debug.id,
            configs=CONFIGS
        )
    # Generate documentation if --pydoc flag is passed
    if args.pydoc:
        # Base documentation folder should be 'docs/pydoc'
        base_path = os.path.join(
            project_path,
            'docs',
            'pydoc'
        )
        log_utils.log_message(
            f'\n[INFO] Project documentation: {project_path}',
            environment.category.info.id,
            configs=CONFIGS
        )
        file_extensions = [".py"]  ## Defined by CLI flag
        ignore_list = ["conftest.py", "tests/mocks", ".pydocs/*"]  # ✅ Ignore conftest.py & test-related paths
        # files_list = collect_files(
        #     project_path,
        #     file_extensions
        # )
        files_list = collect_files(
            target_dir=project_path,
            extensions=file_extensions,
            ignore_list=ignore_list
        )

        pydoc_engine.create_pydocs(
            project_path=project_path,
            base_path=base_path,
            files_list=files_list,
            configs=CONFIGS
        )
        log_utils.log_message(
            f'\n[INFO] Documentation completed successfully.',
            environment.category.info.id,
            configs=CONFIGS
        )
        # Finalize coverage tracking if enabled
        if cov and args.coverage:
            cov.stop()
            cov.save()
            docs_coverage = Path("docs") / "coverage"
            # Check if coverage files exist before combining
            coverage_files = list(Path(docs_coverage).rglob("*.coverage"))
            # f'[INFO] Found coverage files:\n' + "\n".join(f"  - {str(file).replace(f'{docs_coverage}/', '', 1)}" for file in coverage_files) + '\n'
            files_listing = "\n".join(f'  - {str(file).replace(f"{docs_coverage}/", "", 1)}' for file in coverage_files )
            log_utils.log_message(
                f'[INFO] Found coverage files:\n{files_listing}\n',
                environment.category.info.id,
                configs=CONFIGS
            )
            if coverage_files:
                if Path(".coverage").exists() and Path(".coverage").stat().st_size > 0:
                    subprocess.run(
                        ["python", "-m", "coverage", "combine"],
                        check=True
                    )
                    log_utils.log_message(
                        f'Generating Coverage Report ...',
                        environment.category.debug.id,
                        configs=CONFIGS
                    )
                    try:
                        htmlcov_dir = Path("docs") / "htmlcov"
                        htmlcov_dir.mkdir(parents=True, exist_ok=True)
                        subprocess.run(
                            ["python", "-m", "coverage", "html", "-d", str(htmlcov_dir)],
                            check=True
                        )
                        # log_utils.log_message(
                        #     f'Coverage HTML report generated successfully.',
                        #     environment.category.debug.id,
                        #     configs=CONFIGS
                        # )
                    except subprocess.CalledProcessError as e:
                        log_utils.log_message(
                            f'[ERROR] Failed to generate coverage report: {e}',
                            environment.category.error.id,
                            configs=CONFIGS
                        )
                    ## Generate Coverage-Report Summary
                    coverage_report = Path(docs_coverage) / "coverage.report"
                    # log_utils.log_message(
                    #     f"Generating Coverage Report...",
                    #     environment.category.debug.id,
                    #     configs=CONFIGS
                    # )
                    ## Execute Coverage Report and save output to file
                    pydoc_engine.generate_report(
                        coverage_report=coverage_report,
                        configs=CONFIGS
                    )
                    log_utils.log_message(
                        f'Coverage summary saved: {coverage_report}',
                        environment.category.debug.id,
                        configs=CONFIGS
                    )
                    # Read the file and print its content
                    with open(coverage_report, "r", encoding="utf-8") as summary_file:
                        coverage_output = summary_file.read()
                    log_utils.log_message(
                        f'\nCoverage Report:\n{coverage_output}',
                        environment.category.info.id,
                        configs=CONFIGS
                    )
                else:
                    log_utils.log_message(
                        f'[WARNING] No coverage data found. Skipping HTML report.',
                        environment.category.warning.id,
                        configs=CONFIGS
                    )
    # If --target flag is passed, execute the specified Package/Module or Script
    if args.target:
        log_utils.log_message(
            f'Running Package/Module {args.target} ...',
            environment.category.debug.id,
            configs=CONFIGS
        )
        subprocess.run(
            [sys.executable, '-m', args.target]
        )
    # # If no flags, print a basic message
    # log_utils.log_message(
    #     f'No flags provided. Use --pydoc to generate documentation or --target to run a Package/Module or Script.',
    #     environment.category.debug.id,
    #     configs=CONFIGS
    # )

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()

    # print(f'Module Docstring:\n{__doc__}')
    #
    # print(f'parse_arguments.__doc__:\n{parse_arguments.__doc__}')
    # print(f'collect_files.__doc__:\n{collect_files.__doc__}')
