#!/usr/bin/env python3

# Python File: ./packages/requirements/lib/__init__.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/requirements/lib/__init__.py

Description:
    The __init__.py file serves as the entry point for the 'lib' package, integrating multiple
    utility modules responsible for dependency management within the requirements system.

Core Features:
    - **Module Initialization**:
      - Ensures all submodules (`brew_utils`, `package_utils`, `policy_utils`, `version_utils`) are properly imported.
      - Dynamically adjusts `sys.path` for module resolution.
    - **Structured Package Management**:
      - Provides a unified interface for handling Homebrew, Pip, and system-wide package dependencies.
      - Simplifies version tracking and policy enforcement across different package managers.
    - **Dynamic Documentation Loading**:
      - Uses `pydoc_loader` to inject external documentation at runtime.

Usage:
    Importing the module automatically loads all submodules:
        from packages.requirements.lib import brew_utils, package_utils, policy_utils, version_utils

    Example usage:
        from packages.requirements.lib.package_utils import install_requirements
        install_requirements(configs)

    Checking Installed Packages:
        from packages.requirements.lib.version_utils import installed_version
        version = installed_version("requests", configs)

Dependencies:
    - sys - Handles system-level functions such as modifying `sys.path`.
    - pathlib - Ensures platform-independent file path resolution.
    - lib.pydoc_loader - Dynamically loads module documentation.
    - brew_utils - Handles Homebrew-specific package management.
    - package_utils - Provides functions for package installation and backup.
    - policy_utils - Enforces policy-driven package installations.
    - version_utils - Retrieves installed and latest package versions.

Expected Behavior:
    - Automatically exposes core submodules for streamlined package management.
    - Ensures all required dependencies are correctly resolved before module execution.
    - Loads documentation dynamically to maintain clean, structured code.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to missing submodules, system path errors, or incorrect module initialization.
"""

FUNCTION_DOCSTRINGS = {
    "load_pydocs": """
    Function: load_pydocs(script_path: str, module: ModuleType) -> None
    Description:
        Loads and applies documentation dynamically from `.pydoc` files.

    Parameters:
        - script_path (str): The full path of the script whose documentation should be loaded.
        - module (ModuleType): The module in which function and variable docstrings should be applied.

    Returns:
        - None: Modifies the module's docstrings dynamically at runtime.

    Behavior:
        - Searches for a `.pydoc` file matching the script's name.
        - Loads module, function, and variable docstrings from the `.pydoc` file.
    """
}
