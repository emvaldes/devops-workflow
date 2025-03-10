#!/usr/bin/env python3

# Python File: ./lib/pydoc_loader.py
__version__ = "0.1.0"  # Documentation version

"""
Overview
    The `pydoc_loader.py` module is responsible for dynamically loading documentation for Python scripts
    from external `.pydoc` files. This allows scripts to remain clean from embedded docstrings while still
    supporting rich documentation that is accessible via tools like `pydoc` and `help()`.

Core Features:
    - Dynamic Documentation Loading: Loads `.pydoc` files and assigns docstrings dynamically.
    - Function-Level Docstring Assignment: Ensures function docstrings are correctly applied to the target module.
    - Module-Level Documentation Injection: Injects the module docstring at runtime.
    - Variable and Object Documentation: Captures and assigns documentation for global variables and objects.
    - Error Handling & Debugging Support: Provides detailed logs to assist in debugging documentation loading issues.

Expected Behavior & Usage:
    Loading Documentation in a Python Script:
        from lib.pydoc_loader import load_pydocs
        load_pydocs(__file__, sys.modules[__name__])

    Checking Documentation with pydoc:
        python -m pydoc my_script
"""

import sys
import importlib.util

from types import ModuleType
from typing import Dict
from pathlib import Path

def load_pydocs(script_path: str, module: ModuleType) -> None:
    """
    Loads module-level, function-level, and variable-level documentation from an external `.pydoc` file.

    Parameters:
        script_path (str): The full path of the script whose documentation should be loaded.
        module (ModuleType): The module in which function and variable docstrings should be applied.

    Behavior:
        - Searches for a `.pydoc` file matching the script's name in the `.pydocs/` directory.
        - Loads and parses the module docstring (`MODULE_DOCSTRING`), function docstrings (`FUNCTION_DOCSTRINGS`),
          and variable docstrings (`VARIABLE_DOCSTRINGS`).
        - Assigns function and variable docstrings dynamically to the specified module.
        - Does **not** return `MODULE_DOCSTRING`, `FUNCTION_DOCSTRINGS`, or `VARIABLE_DOCSTRINGS` to prevent them
          from appearing as global variables in `pydoc` output.
    """

    script_name = Path(script_path).stem
    pydoc_dir = Path(script_path).resolve().parent / ".pydocs"
    pydoc_path = pydoc_dir / f"pydoc.{script_name}.py"

    if not pydoc_path.exists():
        print(f"⚠️ No .pydoc file found at {pydoc_path}.")
        return

    try:
        spec = importlib.util.spec_from_file_location(f"pydoc_{script_name}", str(pydoc_path))

        if spec is None or spec.loader is None:
            raise ImportError(f"⚠️ Could not load {pydoc_path}")

        pydoc_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pydoc_module)

        # Assign module docstring
        module.__doc__ = getattr(pydoc_module, "MODULE_DOCSTRING", "No module documentation available.")

        # Apply function and variable docstrings
        apply_docstrings(module, getattr(pydoc_module, "FUNCTION_DOCSTRINGS", {}))
        apply_variable_docstrings(module, getattr(pydoc_module, "VARIABLE_DOCSTRINGS", {}))

    except Exception as e:
        print(f"Failed to load .pydoc file: {e}")

def apply_docstrings(module: ModuleType, function_docs: Dict[str, str]) -> None:
    """
    Dynamically assigns function docstrings from a loaded `.pydoc` file to a given module.

    Parameters:
        module (ModuleType): The module in which function docstrings should be applied.
        function_docs (Dict[str, str]): A dictionary mapping function names to their respective docstrings.
    """
    if not isinstance(module, ModuleType):
        print("⚠️ Invalid module provided for docstring application.")
        return

    for func_name, docstring in function_docs.items():
        if hasattr(module, func_name):
            getattr(module, func_name).__doc__ = docstring
        else:
            print(f"⚠️ Function {func_name} not found in module {module.__name__}.")

def apply_variable_docstrings(module: ModuleType, variable_docs: Dict[str, str]) -> None:
    """
    Stores variable docstrings in a global dictionary instead of modifying __doc__,
    since primitive types (str, int, list, etc.) do not support docstring assignment.

    Parameters:
        module (ModuleType): The module in which variable docstrings should be applied.
        variable_docs (Dict[str, str]): A dictionary mapping variable names to their respective descriptions.

    Behavior:
        - Stores variable docstrings in a separate dictionary for retrieval.
        - Ensures variables that cannot have __doc__ modified still have documentation available.
    """

    global VARIABLE_DOCSTRINGS
    VARIABLE_DOCSTRINGS = {}  # ✅ Store variable docstrings here

    for var_name, docstring in variable_docs.items():
        if hasattr(module, var_name):
            obj = getattr(module, var_name)
            VARIABLE_DOCSTRINGS[var_name] = docstring  # ✅ Safe for all variable types
        # else:
        #     print(f"⚠️ Variable {var_name} not found in module {module.__name__}.")

def main() -> None:
    pass

if __name__ == "__main__":
    main()
