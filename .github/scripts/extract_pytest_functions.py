#!/usr/bin/env python3

## File: .github/scripts/extract_pytest_functions.py
## Version: 0.0.2

import re
import json
import sys
import os

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
        if not os.path.isfile( file ):
            print(
                f"Warning: File not found - {file}",
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
                f"Warning: Failed to parse {file} - {str(e)}",
                file=sys.stderr
            )

    return pytest_functions


def validate_json_output(pytest_mapping):
    """
    Validates that the generated JSON file exists and has the correct structure.

    Args:
        pytest_mapping (str): Path to the JSON output file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """

    invalid_structure = f'Error: Invalid JSON structure in "{pytest_mapping}".'
    invalid_jsondata = f'Error: JSON file "{pytest_mapping}" contains invalid JSON.'

    malformed_entries = f'Error: Malformed entry in "pytest_functions":'
    unexpected_issue = f'Error: Unexpected issue reading "{pytest_mapping}":'

    if not os.path.isfile(pytest_mapping):
        print(
            f'Error: Output file "{pytest_mapping}" was not created.',
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

    except json.JSONDecodeError:
        print(
            invalid_jsondata,
            file=sys.stderr
        )
    except Exception as e:
        print(
            f'{unexpected_issue} {str(e)}',
            file=sys.stderr
        )

    return False


def main():
    """
    Main function to handle argument parsing and execution flow.
    """
    script_name = os.path.basename(__file__)

    if len(sys.argv) != 3:
        print(f"Usage: {script_name} <pytest_listing> <pytest_mapping>", file=sys.stderr)
        sys.exit(1)

    pytest_listing = sys.argv[1]
    pytest_mapping = sys.argv[2]

    if pytest_mapping is None:
        pytest_mapping = "pytest_functions.json"

    # print( f'\nPyTests JSON-list:\n{pytest_listing}' )
    # print( f'\nOutput Filename: {pytest_mapping}\n' )

    invalid_listing = f'Error: Invalid Files/Functions JSON input.'
    invalid_functions = f'Error: No valid test functions found.'

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
        # pytest_functions["dummy_test"] = ["dummy_test_function"]
        print(
            invalid_functions,
            file=sys.stderr
        )
        sys.exit(1)

    json_output = {"pytest_functions": pytest_functions}

    ## Export/Save json-output to file
    with open(
        pytest_mapping,
        "w",
        encoding="utf-8"
    ) as out_f:
        json.dump(
            json_output,
            out_f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True
        )
    ## Print final JSON output
    # print(json.dumps(json_output, indent=2, ensure_ascii=False, sort_keys=True))

    if not validate_json_output(pytest_mapping):
        sys.exit(1)

if __name__ == "__main__":
    main()
