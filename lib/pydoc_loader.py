#!/usr/bin/env python3

# Python File: ./lib/pydoc_loader.py
__version__ = "0.1.0"  # Documentation version

"""
File Path: ./lib/pydoc_loader.py

Description:
    The pydoc_loader.py module is responsible for dynamically loading external documentation for Python modules.
    It assigns module-level, function-level, and variable-level docstrings from `.pydoc` files, ensuring scripts
    remain clean from embedded documentation while still providing comprehensive API descriptions.

Core Features:
    - **Dynamic Documentation Loading**: Reads `.pydoc` files and assigns docstrings to functions and variables.
    - **Function-Level Docstring Injection**: Ensures functions have assigned documentation at runtime.
    - **Module-Level Documentation Assignment**: Injects module docstrings dynamically.
    - **Variable Docstring Storage**: Stores variable descriptions separately for retrieval.
    - **Error Handling and Debugging Support**: Provides warnings and logs to assist in debugging docstring application.

Usage:
    Applying Documentation in a Python Script:
        from lib.pydoc_loader import load_pydocs
        load_pydocs(__file__, sys.modules[__name__])

    Checking Documentation with pydoc:
        python -m pydoc my_script

Dependencies:
    - sys - Accesses runtime module references.
    - importlib.util - Dynamically loads external Python modules.
    - types.ModuleType - Provides type hints for module-level docstring assignment.
    - typing.Dict - Defines dictionary type hints for function and variable docstrings.
    - pathlib - Ensures safe and platform-independent file path resolution.

Global Behavior:
    - Dynamically assigns documentation at runtime.
    - Searches for and loads `.pydoc` files located in the `.pydocs/` directory.
    - Ensures function and variable docstrings are correctly applied to modules.
    - Provides warnings if documentation files are missing.

CLI Integration:
    This module is designed as a helper utility for other scripts but can be manually tested.

Example Execution:
    python pydoc_loader.py

Expected Behavior:
    - Successfully loads `.pydoc` documentation files.
    - Assigns function and variable docstrings dynamically.
    - Logs missing documentation files with warnings.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Error encountered during documentation loading.
"""

# Standard library imports - Core system module
import sys
import importlib.util

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Type-related modules
from types import ModuleType
from typing import Dict

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def load_pydocs(script_path: str, module: ModuleType) -> None:
    """
    Function: load_pydocs(script_path: str, module: ModuleType) -> None
    Description:
        Loads external documentation from a `.pydoc` file and applies it to a given module.

    Parameters:
        - script_path (str): The absolute path of the script whose documentation should be loaded.
        - module (ModuleType): The module where function and variable docstrings should be applied.

    Behavior:
        - Searches for a `.pydoc` file matching the script name in the `.pydocs/` directory.
        - Loads and parses the module docstring (`MODULE_DOCSTRING`), function docstrings (`FUNCTION_DOCSTRINGS`),
          and variable docstrings (`VARIABLE_DOCSTRINGS`).
        - Assigns function and variable docstrings dynamically to the target module.

    Error Handling:
        - Logs a warning if no corresponding `.pydoc` file is found.
        - Logs an error if the `.pydoc` file fails to load or parse.
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
    Function: apply_docstrings(module: ModuleType, function_docs: Dict[str, str]) -> None
    Description:
        Dynamically assigns function docstrings from an external `.pydoc` file to a given module.

    Parameters:
        - module (ModuleType): The module where function docstrings should be applied.
        - function_docs (Dict[str, str]): A dictionary mapping function names to their respective docstrings.

    Behavior:
        - Iterates through the dictionary of function docstrings.
        - Assigns each docstring to the corresponding function in the target module.

    Error Handling:
        - Logs a warning if a function does not exist in the module.
    """
    if not isinstance(module, ModuleType):
        print("⚠️ Invalid module provided for docstring application.")
        return

    for func_name, docstring in function_docs.items():
        if hasattr(module, func_name):
            getattr(module, func_name).__doc__ = docstring
        # else:
        #     print(f"⚠️ Function {func_name} not found in module {module.__name__}.")

def apply_variable_docstrings(module: ModuleType, variable_docs: Dict[str, str]) -> None:
    """
    Function: apply_variable_docstrings(module: ModuleType, variable_docs: Dict[str, str]) -> None
    Description:
        Stores variable docstrings in a dictionary instead of modifying `__doc__`, as primitive types
        (str, int, list, etc.) do not support direct docstring assignments.

    Parameters:
        - module (ModuleType): The module where variable docstrings should be applied.
        - variable_docs (Dict[str, str]): A dictionary mapping variable names to their respective descriptions.

    Behavior:
        - Stores variable docstrings in a global dictionary for easy retrieval.
        - Ensures that variables without `__doc__` support are documented separately.

    Error Handling:
        - Logs a warning if a variable is not found in the module.
    """

    global VARIABLE_DOCSTRINGS
    VARIABLE_DOCSTRINGS = {}  # Store variable docstrings here

    for var_name, docstring in variable_docs.items():
        if hasattr(module, var_name):
            obj = getattr(module, var_name)
            VARIABLE_DOCSTRINGS[var_name] = docstring  # Safe for all variable types
        # else:
        #     print(f"⚠️ Variable {var_name} not found in module {module.__name__}.")

def main() -> None:
    """
    Function: main() -> None
    Description:
        Placeholder function for module execution.
    """

    pass

if __name__ == "__main__":
    main()
