#!/usr/bin/env python3

## File: .github/scripts/extract_pytest_functions.py
## Version: 0.0.2

import sys
import os

import re
import json

from pathlib import Path

def extract_pytest_functions(pytest_files):
    """
    Extracts function names that match the pytest naming pattern from the provided test files.

    Args:
        pytest_files (list): List of pytest test files to process.

    Returns:
        dict: A dictionary where keys are file paths, and values are lists of extracted function names.
    """

    pytest_functions = {}

    ## Processing all target pytest-files
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
                pytest_functions[file] = functions
        except Exception as e:
            print(
                f'Warning: Failed to parse {file} - {str(e)}',
                file=sys.stderr
            )

    ## Identifies if pytest_resources exist
    if not pytest_functions:
        return False

    ## Construct final JSON output
    json_output = {"pytest_functions": pytest_functions}

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
            or "pytest_functions" not in data
            or not isinstance(data["pytest_functions"], dict)
        ):
            print(
                invalid_structure,
                file=sys.stderr
            )
            return False

        ## Ensure all keys in "pytest_functions" are filenames with list values
        for file, functions in data["pytest_functions"].items():
            if not isinstance(file, str) or not isinstance(functions, list):
                print(
                    f'{malformed_entries} {file} -> {functions}',
                    file=sys.stderr
                )
                return False

        return True

        ## Ensure the content is not empty
        if not data["pytest_functions"]:
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
    invalid_functions = f'[ERROR] No valid test functions found.'

    ## Importing pytest-files listing
    try:
        pytest_files = json.loads(pytest_listing)
    except json.JSONDecodeError:
        print(
            invalid_listing,
            file=sys.stderr
        )
        sys.exit(1)

    pytest_functions = extract_pytest_functions(pytest_files)

    ## Identifies if pytest_functions exist
    if not pytest_functions:
        print(
            invalid_functions,
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
            pytest_functions,
            out_f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True
        )

    ## Print final JSON output
    # print(json.dumps(pytest_functions, indent=2, ensure_ascii=False, sort_keys=True))

    if not validate_json_output(pytest_mapping):
        sys.exit(1)

    # print(
    #     f"Validation successful: '{pytest_mapping}' exists and is correctly formatted."
    # )

if __name__ == "__main__":
    main()
