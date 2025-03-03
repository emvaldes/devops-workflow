#!/usr/bin/env python3

# File: .github/scripts/extract_pytest_resources.py
# Version: 0.0.2

"""
File Path: .github/scripts/extract_pytest_resources.py

Description:

PyTest Resource Extractor

This module scans a list of pytest test files, extracts function names following
the pytest naming convention, and stores the results in JSON format.

Core Features:

- **Automatic PyTest Resource Extraction**: Identifies test function definitions.
- **Relative Path Resolution**: Normalizes file paths to a base location.
- **Structured Output**: Saves extracted resources in a structured JSON format.
- **File Validation**: Ensures that all input test files exist before processing.
- **Error Handling**: Logs warnings for missing or unreadable files instead of failing abruptly.
- **JSON Integrity Check**: Validates the output JSON file after writing.

Primary Functions:

- `extract_pytest_resources(pytest_files)`: Reads and processes pytest files.
- `validate_json_output(pytest_mapping)`: Ensures the JSON file exists and follows the expected structure.

Expected Behavior:

- If an input file is missing, a warning is displayed, but execution continues.
- If no valid test functions are found, an error message is logged.
- JSON output is validated to prevent incorrect or malformed results.
- The script exits with an appropriate status code based on the success or failure of extraction.

Dependencies:

- `re` (for regex-based function extraction)
- `json` (for structured output)
- `sys`, `os` (for file and argument handling)

Usage:

To extract pytest resources from a JSON list of test files and save them to an output JSON file:
> python .github/scripts/extract_pytest_resources.py '<pytest_listing>' '<pytest_mapping>'

Example:
> python .github/scripts/extract_pytest_resources.py '["test_example.py"]' "pytest_resources.json"

"""

import sys
import os

import re
import json

from pathlib import Path

def extract_pytest_resources(pytest_files):
    """
    Extracts function names that match the pytest naming pattern from the provided test files.

    Args:
        pytest_files (list): List of pytest test files to process.

    Returns:
        dict: A dictionary where keys are file paths, and values are lists of extracted function names.
    """

    pytest_resources = []

    ## Processing all target pytest-files
    if not pytest_files:
        return {}

    # Determine base location from the provided files
    if len(pytest_files) == 1:
        ## If only one file, set its directory as the location
        base_location = os.path.dirname(pytest_files[0])
    else:
        base_location = os.path.commonpath(pytest_files)

    # Processing all target pytest files
    for file in pytest_files:
        if not os.path.isfile(file):
            print(
                f'Warning: File not found - {file}',
                file=sys.stderr
            )
            continue
        try:
            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:
                content = f.read()
                ## Extract test function names using regex
                functions = re.findall(
                    r'^def (test_[a-zA-Z0-9_]+)',
                    content,
                    re.MULTILINE
                )
            if functions:
                ## Convert absolute file path to relative path based on base_location
                relative_file = os.path.relpath(file, base_location)
                pytest_resources.append(
                    {"file": relative_file, "functions": functions}
                )
        except Exception as e:
            print(
                f'Warning: Failed to parse {file} - {str(e)}',
                file=sys.stderr
            )

    ## Identifies if pytest_resources exist
    if not pytest_resources:
        return False

    ## Construct final JSON output
    json_output = {"location": base_location, "resources": pytest_resources}

    return json_output

def validate_json_output(pytest_mapping):
    """
    Validates that the generated JSON file exists and has the correct structure.

    Args:
        pytest_mapping (str): Path to the JSON output file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """

    invalid_structure = f'[ERROR] Invalid JSON structure in "{pytest_mapping}".'
    invalid_jsondata = f'[ERROR] JSON file "{pytest_mapping}" contains invalid JSON.'
    invalid_output = f'[ERROR] Output JSON in "{pytest_mapping}" contains no extracted functions.'

    malformed_entries = f'[ERROR] Malformed entry in "pytest_functions":'
    unexpected_issue = f'[ERROR] Unexpected issue reading "{pytest_mapping}":'

    outputfile_notcreated = f'[ERROR] Output file "{pytest_mapping}" was not created.'
    outputfile_isempty = f'[ERROR] Output file "{pytest_mapping}" is empty.'
    outputfile_lastmodified = f'[INFO] Output file "{pytest_mapping}" last modified at'

    ## Validate the JSON file exists and structure is correct
    if not os.path.isfile(pytest_mapping):
        print(
            outputfile_notcreated,
            file=sys.stderr
        )
        return False

    ## Ensure the file is non-empty
    if os.path.getsize(pytest_mapping) == 0:
        print(
            outputfile_isempty,
            file=sys.stderr
        )
        return False

    try:
        with open(
            pytest_mapping,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        ## Ensure JSON structure is correct
        if (
            not isinstance(data, dict)
            or "location" not in data
            or "resources" not in data
            or not isinstance(data["resources"], list)
        ):
            print(
                invalid_structure,
                file=sys.stderr
            )
            return False

        ## Ensure all resources have correct structure
        for entry in data["resources"]:
            if not isinstance(entry, dict) or "file" not in entry or "functions" not in entry:
                print(
                    f'{malformed_entries}: {entry}',
                    file=sys.stderr
                )
                return False

        return True

        ## Ensure the content is not empty
        if not data["resources"]:
            print(
                invalid_output,
                file=sys.stderr
            )
            return False

        ## Confirm file modification timestamp
        last_modified = os.path.getmtime(pytest_mapping)
        print(
            f'{outputfile_lastmodified}: {last_modified}'
        )
        return True

    except json.JSONDecodeError:
        print(
            invalid_jsondata,
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(
            f'{unexpected_issue} {str(e)}',
            file=sys.stderr
        )
        sys.exit(1)

    return False

def main():
    """
    Main function to handle argument parsing and execution flow.
    """

    script_name = os.path.basename(__file__)

    if len(sys.argv) != 3:
        print(
            f'Usage: {script_name} <pytest_listing> <pytest_mapping>',
            file=sys.stderr
        )
        sys.exit(1)

    pytest_listing = sys.argv[1]
    pytest_mapping = sys.argv[2]

    if pytest_mapping is None:
        pytest_mapping = "pytest_functions.json"

    # print( f'\nPyTests JSON-list:\n{pytest_listing}' )
    # print( f'\nOutput Filename: {pytest_mapping}\n' )

    invalid_listing = f'[ERROR] Invalid Files/Functions JSON input.'
    invalid_resources = f'[ERROR] No valid test functions found.'

    ## Importing pytest-files listing
    try:
        pytest_files = json.loads(pytest_listing)
    except json.JSONDecodeError:
        print(
            invalid_listing,
            file=sys.stderr
        )
        sys.exit(1)

    pytest_resources = extract_pytest_resources(pytest_files)

    ## Identifies if pytest_functions exist
    if not pytest_resources:
        print(
            invalid_resources,
            file=sys.stderr
        )
        sys.exit(1)

    ## Export/Save json-output to file
    with open(
        pytest_mapping,
        "w",
        encoding="utf-8"
    ) as out_f:
        json.dump(
            pytest_resources,
            out_f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True
        )

    ## Print final JSON output
    # print(json.dumps(pytest_resources, indent=2, ensure_ascii=False, sort_keys=True))

    if not validate_json_output(pytest_mapping):
        sys.exit(1)

    # print(
    #     f"Validation successful: '{pytest_mapping}' exists and is correctly formatted."
    # )

if __name__ == "__main__":
    main()
