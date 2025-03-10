import importlib.util
from pathlib import Path

pydoc_path = Path("/Users/emvaldes/.repos/devops/workflows/tests/requirements/dependencies/brew_utils/test_brew_utils.pydoc")

print(f"Resolved Path: {pydoc_path}")

print(f"Attempting to import {pydoc_path} as a Python module...")

spec = importlib.util.spec_from_file_location("doc_module", str(pydoc_path))

if spec is None:
    print("❌ `spec_from_file_location()` failed! Path issue likely.")
elif spec.loader is None:
    print("❌ `spec.loader` is None! Something is wrong with the file format.")
else:
    try:
        doc_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_module)
        print("✅ Module loaded successfully!")
        print(f"MODULE_DOCSTRING: {getattr(doc_module, 'MODULE_DOCSTRING', 'Not found')}")
        print(f"FUNCTION_DOCSTRINGS: {getattr(doc_module, 'FUNCTION_DOCSTRINGS', 'Not found')}")
    except Exception as e:
        print(f"❌ Failed to execute module: {e}")
