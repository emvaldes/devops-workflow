#!/usr/bin/env python3

## File: .github/scripts/extract-pytest-functions.py
## Version: 0.0.1

import re
import json
import sys
import os

script_name = os.path.basename(__file__)

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

# pytest_functions = {}
pytest_resources = []

## Determine base location from the provided files
if len(pytest_files) == 1:
    ## If only one file, set its directory as the location
    single_file_path = pytest_files[0]
    base_location = os.path.dirname(single_file_path)
else:
    ## Otherwise, find the common directory for all files
    base_location = os.path.commonpath(pytest_files)

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
            # pytest_functions[file] = functions
            ## Convert absolute file path to relative path based on base_location
            relative_file = os.path.relpath(file, base_location)
            pytest_resources.append({"file": relative_file, "functions": functions})
    except Exception as e:
        print(
            f"Warning: Failed to parse {file} - {str(e)}",
            file=sys.stderr
        )

## Identifies if pytest_resources exist
# if not pytest_functions:
#     # pytest_functions["dummy_test"] = ["dummy_test_function"]
if not pytest_resources:
    print(
        invalid_content,
        file=sys.stderr
    )
    sys.exit(1)
else:
    ## Construct final JSON output
    # json_output = {"pytest_functions": pytest_functions}
    json_output = {"location": base_location, "resources": pytest_resources}

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
        # or "pytest_functions" not in data
        # or not isinstance( data["pytest_functions"], dict )
        or "location" not in data
        or "resources" not in data
        or not isinstance( data["resources"], list )
    ):
        print(
            f"Error: Invalid JSON structure in '{pytest_mapping}'.",
            file=sys.stderr
        )
        sys.exit(1)
    ## Ensure all resources have correct structure
    # for file, functions in data["pytest_functions"].items():
    #     if not isinstance( file, str ) or not isinstance( functions, list ):
    for entry in data["resources"]:
        if not isinstance( entry, dict ) or "file" not in entry or "functions" not in entry:
            print(
                # f"Error: Malformed entry in 'pytest_functions': {file} -> {functions}",
                f"Error: Malformed entry in 'resources': {entry}",
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
