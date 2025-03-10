#!/usr/bin/env python3

# Python File: ./packages/requirements/lib/policy_utils.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
File Path: ./packages/requirements/lib/policy_utils.py

Description:
    The policy_utils.py module provides structured policy evaluation for package management.
    It ensures that packages are installed, upgraded, or downgraded according to predefined policies.

Core Features:
    - Policy-Based Dependency Evaluation: Determines whether a package should be installed, upgraded, downgraded, or skipped.
    - Automated Compliance Checking: Compares installed versions against target and latest versions.
    - Dynamic Policy Enforcement: Adapts installation actions based on policies such as "latest" or "restricted".
    - Structured Logging: Provides detailed debugging and compliance logs for traceability.
    - Integration with Installed Package Records: Updates installed.json dynamically.

Usage:
    Evaluating Package Policies:
        from packages.requirements.lib.policy_utils import policy_management
        updated_packages = policy_management(configs)

    Checking a Specific Package Status:
        from packages.requirements.lib.version_utils import installed_version
        current_version = installed_version("requests", configs)

Dependencies:
    - sys - Handles system-level functions such as process termination.
    - subprocess - Executes shell commands for package management.
    - json - Handles structured dependency files.
    - importlib.metadata - Retrieves installed package versions.
    - functools.lru_cache - Caches function calls for efficiency.
    - pathlib - Ensures platform-independent file path resolution.
    - packages.appflow_tracer.lib.log_utils - Provides structured logging.
    - package_utils - Retrieves installed.json and manages package installation.
    - version_utils - Retrieves installed and latest package versions.

Expected Behavior:
    - Ensures all required packages follow policy-based installation decisions.
    - Prevents unintended upgrades/downgrades when policy is set to "restricted".
    - Logs all policy enforcement actions for debugging and compliance tracking.

Exit Codes:
    - 0: Execution completed successfully.
    - 1: Failure due to missing configurations, package errors, or policy conflicts.
"""

FUNCTION_DOCSTRINGS = {
    "policy_management": """
    Function: policy_management(configs: dict) -> list
    Description:
        Evaluates package installation policies and updates dependency statuses.

    Parameters:
        - configs (dict): The configuration dictionary containing dependency policies.

    Returns:
        - list: The updated list of dependencies with policy-based statuses.

    Behavior:
        - Analyzes installed packages and determines policy actions (install, upgrade, downgrade, or skip).
        - Updates `installed.json` with the latest package states.
        - Logs compliance decisions for debugging and tracking.

    Policy Decision Logic:
        1. **Missing Package (status = "installing")**
           - Installs the package as per policy (either latest or target version).

        2. **Outdated Package (status = "outdated" | "upgrading")**
           - If installed version < target version:
             - "latest" policy → Upgrade to latest available version.
             - "restricted" policy → Keep outdated but log a warning.

        3. **Target Version Matched (status = "matched")**
           - If installed version == target version:
             - "latest" policy → Check for newer versions and mark as "outdated".
             - Otherwise, mark as "matched" (no action needed).

        4. **Upgraded Version Installed (status = "downgraded" | "upgraded")**
           - If installed version > target version:
             - "restricted" policy → Downgrade to target version.
             - "latest" policy → Keep upgraded.

    Error Handling:
        - Logs policy violations or missing configurations.
        - Ensures structured compliance before initiating installation processes.
    """,
}
