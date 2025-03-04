#!/usr/bin/env python3

# File: .github/scripts/extract_pytest_functions.py
# Version: 0.1.0

"""
File: .github/scripts/extract_pytest_functions.py
Version: 0.0.2

Description:
    This script scans a given list of pytest test files and extracts function names
    that conform to pytest's test naming convention (`test_*`). The extracted function names
    are stored in a structured JSON file.

    The script also performs validation to ensure the generated JSON file adheres to
    the expected format and contains valid function mappings.

Features:
    - Reads a JSON list of pytest test files.
    - Extracts valid test function names from each file using regex.
    - Saves the extracted function mappings to a JSON output file.
    - Validates the JSON output to ensure correctness and completeness.

Usage:
    python extract_pytest_functions.py <pytest_listing> <pytest_mapping>

Arguments:
    pytest_listing (str): A JSON-encoded list containing paths to pytest test files.
    pytest_mapping (str): The output JSON file where extracted function names will be stored.

Exit Codes:
    1 - An error occurred (invalid input, missing files, extraction failure, validation failure, etc.).
    0 - Success, extracted test functions are stored correctly.

Requirements:
    - Python 3.x
    - JSON-formatted input for pytest test files
    - Read access to the provided test files

Example:
    ```bash
    python extract_pytest_functions.py '["tests/test_example.py"]' "pytest_functions.json"
    ```

Output Format:
    The JSON file follows this structure:
    ```json
    {
        "pytest_functions": {
            "tests/test_example.py": ["test_addition", "test_subtraction"]
        }
    }
    ```
"""

# Package version
__version__ = "0.1.0"

import sys
import os

import re
import json

from typing import List, Dict, Union
from pathlib import Path

def extract_pytest_functions(
    pytest_files: List[str]
) -> Union[Dict[str, List[str]], bool]:
    """
    Extracts pytest test function names from the given list of test files.

    Args:
        pytest_files (List[str]): A list of pytest test file paths to be processed.

    Returns:
        Dict[str, List[str]]: A dictionary where:
            - Keys are file paths of pytest test scripts.
            - Values are lists of extracted function names matching pytest's naming convention.

        bool: Returns False if no valid test functions are found in any file.

    Raises:
        IOError: If a file cannot be opened or read.
        Exception: If an unexpected error occurs while processing the files.

    Extraction Process:
        - Reads each file and searches for function names matching the pattern `test_*`.
        - Uses regex to extract function names: `^def (test_[a-zA-Z0-9_]+)`.
        - Skips unreadable or missing files, issuing warnings instead of failing outright.

    Notes:
        - If no valid functions are found, the function returns `False` instead of an empty dictionary.
        - The output dictionary only includes files that contain at least one valid test function.
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

def validate_json_output(
    pytest_mapping: str
) -> bool:
    """
    Validates the structure and content of the generated JSON output file.

    Args:
        pytest_mapping (str): Path to the JSON file containing pytest function mappings.

    Returns:
        bool:
            - True if the JSON file exists, follows the correct structure, and contains valid data.
            - False if the file is missing, empty, or improperly formatted.

    Raises:
        json.JSONDecodeError: If the JSON file is corrupted or contains invalid JSON.
        IOError: If the file cannot be accessed.
        Exception: If any other unexpected error occurs.

    Validation Process:
        1. Checks if the file exists and is not empty.
        2. Ensures the JSON structure follows the expected format:
           ```json
           {
               "pytest_functions": {
                   "file_path.py": ["test_function_1", "test_function_2"]
               }
           }
           ```
        3. Confirms that extracted function names are stored as lists under corresponding file paths.
        4. Reports malformed entries or structural issues.

    Notes:
        - If the JSON file does not exist or is empty, the function returns `False`.
        - If validation fails, descriptive error messages are printed to stderr.
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

def main() -> None:
    """
    Main function to orchestrate the extraction and validation of pytest test functions.

    Workflow:
        1. Parses command-line arguments.
        2. Reads a JSON-formatted list of pytest test file paths.
        3. Calls `extract_pytest_functions()` to scan the test files.
        4. Saves the extracted function names to a JSON file.
        5. Calls `validate_json_output()` to ensure the output is structured correctly.

    Command-Line Arguments:
        pytest_listing (str): JSON list containing pytest test file paths.
        pytest_mapping (str): Path to save the extracted test function names (JSON).

    Returns:
        None: This function does not return any values. It either exits successfully or terminates with an error.

    Exit Codes:
        1 - Failure (invalid JSON input, missing files, extraction failure, or validation errors).
        0 - Success (functions extracted and validated successfully).

    Notes:
        - If `pytest_mapping` is not specified, it defaults to `"pytest_functions.json"`.
        - If extraction or validation fails, the script exits with status code 1.
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
