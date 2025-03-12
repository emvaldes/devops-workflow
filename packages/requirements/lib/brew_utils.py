#!/usr/bin/env python3

# File: ./packages/requirements/lib/brew_utils.py
# Version: 0.1.0

# Standard library imports - Core system and OS interaction modules
import sys
import subprocess
import shutil

# Standard library imports - Utility modules
import re
import json
import argparse
import platform
import logging

# Standard library imports - Import system
import importlib.metadata

# Standard library imports - Function tools
from functools import lru_cache

# Standard library imports - Date and time handling
from datetime import datetime, timezone

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Type hinting (kept in a separate group)
from typing import Optional, Union

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

## -----------------------------------------------------------------------------

@lru_cache(maxsize=1)  # Cache the result to avoid redundant subprocess calls
def check_availability() -> bool:

    if sys.platform != "darwin":  # Ensure it only runs on macOS
        return False  # Prevents false positives on Ubuntu runners

    # Fast check: If Brew binary is not found, return False immediately
    brew_path = shutil.which("brew")
    if not brew_path:
        return False

    try:
        subprocess.run(
            [ "brew", "--version" ],
            capture_output=True,
            check=True,
            text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

## -----------------------------------------------------------------------------

def brew_info(package: str) -> Optional[str]:

    try:
        result = subprocess.run(
            ["brew", "info", package],
            capture_output=True,
            text=True,
            check=True
        )

        # If error message appears, package does not exist
        if "Error: No formula found" in result.stderr:
            return None

        # Extract the version from Brew's output (first line)
        return result.stdout.split("\n")[0].split()[1]  # Example: "example_package 1.2.3" → "1.2.3"

    except subprocess.CalledProcessError:
        return None  # Return None if the command fails

## -----------------------------------------------------------------------------

def detect_environment() -> dict:

    brew_available = check_availability()

    env_info = {
        "OS": platform.system().lower(),  # "windows", "linux", "darwin" (macOS)
        "INSTALL_METHOD": "standalone",   # Default to standalone Python installation
        "EXTERNALLY_MANAGED": False,      # Assume pip installs are allowed
        "BREW_AVAILABLE": brew_available  # Use precomputed Brew availability
    }

    # Check for EXTERNALLY-MANAGED marker (Linux/macOS)
    external_marker = Path(sys.prefix) / "lib" / f'python{sys.version_info.major}.{sys.version_info.minor}' / "EXTERNALLY-MANAGED"
    if external_marker.exists():
        env_info["EXTERNALLY_MANAGED"] = True

    # If Brew is available, determine if Python is installed via Brew
    if brew_available:
        try:
            result = subprocess.run(
                [ "brew", "--prefix", "python" ],
                capture_output=True,
                text=True,
                check=True
            )
            if result.returncode == 0:
                env_info["INSTALL_METHOD"] = "brew"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Linux: Check if Python is installed via APT (Debian/Ubuntu) or DNF (Fedora)
    elif env_info["OS"] == "linux":
        try:
            result = subprocess.run(["dpkg", "-l", "python3"], capture_output=True, text=True)
            if "python3" in result.stdout:
                env_info["INSTALL_METHOD"] = "system"  # APT-managed
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    [ "rpm", "-q", "python3" ],
                    capture_output=True,
                    text=True
                )
                if "python3" in result.stdout:
                    env_info["INSTALL_METHOD"] = "system"  # DNF-managed
            except FileNotFoundError:
                pass

        # Ensure standalone classification if not system-managed
        if env_info["INSTALL_METHOD"] == "system" and not (Path("/usr/bin/python3").exists() or Path("/usr/local/bin/python3").exists()):
            env_info["INSTALL_METHOD"] = "standalone"

    # Windows: Check if Python is from Microsoft Store
    elif env_info["OS"] == "windows":
        try:
            result = subprocess.run(
                [ "python", "-m", "ensurepip" ],
                capture_output=True,
                text=True,
                check=True
            )
            if "externally-managed-environment" in result.stderr.lower():
                env_info["EXTERNALLY_MANAGED"] = True
                env_info["INSTALL_METHOD"] = "microsoft_store"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return env_info

# ------------------------------------------------------

def version(package: str) -> Optional[str]:

    try:
        result = subprocess.run(
            [ "brew", "list", "--versions", package ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split()[-1] if result.stdout else None
    except subprocess.CalledProcessError:
        return None  # Brew package not found

## -----------------------------------------------------------------------------

def latest_version(package: str) -> Optional[str]:

    # try:
    #     result = subprocess.run(
    #         [ "brew", "info", package ],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #     )
    #     for line in result.stdout.splitlines():
    #         if "stable" in line:
    #             return line.split()[1]  # Extract version
    # except subprocess.CalledProcessError:
    #     return None  # Brew failed

    try:
        result = subprocess.run(
            ["brew", "info", package],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            match = re.search(r"stable (\d+\.\d+\.\d+)", line)
            if match:
                return match.group(1)  # Extract the version number
    except subprocess.CalledProcessError:
        return None  # Brew failed

    return None  # No version found

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

def main() -> None:
    pass

if __name__ == "__main__":
    main()
