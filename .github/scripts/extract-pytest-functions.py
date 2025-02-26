#!/usr/bin/env python3

## File: .github/scripts/extract-pytest-functions.py
## Version: 0.0.1

import re
import json
import sys
import os

# Ensure we received the correct arguments
if len(sys.argv) != 3:
    print("Usage: extract_pytest_functions.py <test_files_json> <output_filename>", file=sys.stderr)
    sys.exit(1)

test_files_json = sys.argv[1]
output_filename = sys.argv[2]

if output_filename is None:
    output_filename = "test_functions.json"

# print( f'\nPyTests JSON-list:\n{test_files_json}' )
# print( f'\nOutput Filename: {output_filename}\n' )

# Convert JSON string to a list
try:
    test_files = json.loads(test_files_json)
except json.JSONDecodeError:
    print("Error: Invalid JSON input for test files.", file=sys.stderr)
    sys.exit(1)

test_functions = {}

for file in test_files:
    if not os.path.isfile(file):
        print(f"Warning: File not found - {file}", file=sys.stderr)
        continue
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            functions = re.findall(r'^def (test_[a-zA-Z0-9_]+)', content, re.MULTILINE)

        if functions:
            test_functions[file] = functions
    except Exception as e:
        print(f"Warning: Failed to parse {file} - {str(e)}", file=sys.stderr)

# Ensure at least one test is present
if not test_functions:
    test_functions["dummy_test"] = ["dummy_test_function"]

json_output = {"test_functions": test_functions}

# Save to output file
with open(output_filename, "w", encoding="utf-8") as out_f:
    json.dump(json_output, out_f, indent=2, ensure_ascii=False, sort_keys=True)

# # Print final JSON output
# print(json.dumps(json_output, indent=2, ensure_ascii=False, sort_keys=True))
