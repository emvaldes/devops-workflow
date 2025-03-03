#!/usr/bin/env python3

## File: .github/scripts/extract_pytest_functions.py
## Version: 0.0.1

"""
File Path: .github/scripts/extract_pytest_functions.py

Description:

PyTest Function Extractor

This module scans a list of pytest test files and extracts function names that match the pytest naming convention.
It saves the extracted function names into a structured JSON file for further processing.

Core Features:

- **Automatic PyTest Function Discovery**: Extracts function names that start with `test_`.
- **Structured Output**: Saves extracted function names in JSON format.
- **File Validation**: Ensures that all input test files exist before processing.
- **Error Handling**: Logs warnings for missing or unreadable files instead of failing abruptly.
- **JSON Integrity Check**: Validates the output JSON file after writing.

Primary Functions:

- `extract_pytest_functions(pytest_listing, pytest_mapping)`: Reads and processes pytest files.
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

To extract pytest function names from a JSON list of test files and save them to an output JSON file:
> python .github/scripts/extract_pytest_functions.py '<pytest_listing>' '<pytest_mapping>'

Example:
> python .github/scripts/extract_pytest_functions.py '["test_example.py"]' "pytest_functions.json"

"""

import re
import json
import sys
import os

from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

script_name = os.path.basename( __file__ )

## Ensure we received the correct arguments
if len( sys.argv ) != 3:
    print(
        f"Usage: {script_name} <pytest_listing> <pytest_mapping>",
        file=sys.stderr
    )
    sys.exit(1)

pytest_listing = sys.argv[1]
pytest_mapping = sys.argv[2]

if pytest_mapping is None:
    pytest_mapping = "pytest_functions.json"

# print( f'\nPyTests JSON-list:\n{pytest_listing}' )
# print( f'\nOutput Filename: {pytest_mapping}\n' )

invalid_content = f"Error: Invalid Files/Functions JSON input."

## Importing pytest-files listing
try:
    pytest_files = json.loads( pytest_listing )
except json.JSONDecodeError:
    print(
        invalid_content,
        file=sys.stderr
    )
    sys.exit(1)

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

## Identifies if pytest_functions exist
if not pytest_functions:
    # pytest_functions["dummy_test"] = ["dummy_test_function"]
    print(
        invalid_content,
        file=sys.stderr
    )
    sys.exit(1)
else:
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

## Validate the JSON file exists and structure is correct
if not os.path.isfile( pytest_mapping ):
    print(
        f"Error: Output file '{pytest_mapping}' was not created.",
        file=sys.stderr
    )
    sys.exit(1)

try:
    with open(
        pytest_mapping,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)
    ## Ensure JSON structure is correct
    if (
        not isinstance( data, dict )
        or "pytest_functions" not in data
        or not isinstance( data["pytest_functions"], dict )
    ):
        print(
            f"Error: Invalid JSON structure in '{pytest_mapping}'.",
            file=sys.stderr
        )
        sys.exit(1)
    ## Ensure all keys in "pytest_functions" are filenames with list values
    for file, functions in data["pytest_functions"].items():
        if not isinstance( file, str ) or not isinstance( functions, list ):
            print(
                f"Error: Malformed entry in 'pytest_functions': {file} -> {functions}",
                file=sys.stderr
            )
            sys.exit(1)
except json.JSONDecodeError:
    print(
        f"Error: JSON file '{pytest_mapping}' contains invalid JSON.",
        file=sys.stderr
    )
    sys.exit(1)
except Exception as e:
    print(
        f"Error: Unexpected issue reading '{pytest_mapping}': {str(e)}",
        file=sys.stderr
    )
    sys.exit(1)

# print(
#     f"Validation successful: '{pytest_mapping}' exists and is correctly formatted."
# )
