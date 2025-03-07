#!/usr/bin/env python3

# File: ./packages/requirements/lib/brew_utils.py
# Version: 0.1.0

"""
# Homebrew Utilities for Dependency Management

## Overview
    This module provides utility functions for integrating Homebrew package management
    within the dependency management system. It facilitates checking the availability
    of Homebrew, detecting Python installation environments, and retrieving installed
    and latest package versions from Homebrew.

## Features
    - **Homebrew Availability Check:** Determines whether Homebrew is installed.
    - **Python Environment Detection:** Identifies how Python is installed (Brew, system, standalone, etc.).
    - **Package Version Retrieval:** Fetches the installed and latest versions of packages managed by Homebrew.

## Usage
    The module is used internally by the dependency management system to dynamically
    detect Python installation methods and ensure compliance with system constraints.

## Dependencies
    - `subprocess`: For executing shell commands.
    - `shutil`: To verify the presence of the `brew` command.
    - `platform`: To determine the operating system.
    - `importlib.metadata`: For alternative package version lookups.
    - `functools.lru_cache`: To optimize repetitive queries.

## Notes
    - This module is optimized for macOS but includes environment detection for Linux and Windows.
    - The `check_availability()` function caches results to minimize system calls.
    - The `detect_environment()` function ensures that externally managed environments are respected.
"""

import sys
import subprocess
import shutil

import json
import argparse
import platform
import logging

import importlib.metadata

from functools import lru_cache

from datetime import datetime, timezone
from typing import Optional, Union

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f'  - {path}')

from lib import system_variables as environment
from packages.appflow_tracer.lib import log_utils

## -----------------------------------------------------------------------------

@lru_cache(maxsize=1)  # Cache the result to avoid redundant subprocess calls
def check_availability() -> bool:
    """
    Check if Homebrew is available on macOS.

    This function determines whether Homebrew is installed and operational. It first
    checks for the existence of the `brew` binary using `shutil.which()`, then
    verifies its functionality by running `brew --version`.

    ## Returns:
        - `bool`:
          - `True` if Homebrew is installed and operational.
          - `False` if Homebrew is unavailable or the system is not macOS.

    ## Notes:
        - Uses `lru_cache(maxsize=1)` to cache the result, avoiding redundant system calls.
        - Returns `False` immediately if the system is not macOS.
    """

    if sys.platform != "darwin":
        return False  # Not macOS, so Brew isn't available

    # Fast check: If Brew binary is not found, return False immediately
    if not shutil.which("brew"):
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

def detect_environment() -> dict:
    """
    Detect the Python installation method and determine if it is externally managed.

    This function examines the system's Python installation method and whether
    package installations are restricted. It identifies installations from:
        - **Homebrew (macOS)**
        - **System package managers (APT/DNF)**
        - **Microsoft Store (Windows)**
        - **Standalone Python installations**

    ## Returns:
        - `dict`: A dictionary containing:
          - `"OS"` (`str`): The detected operating system (`"darwin"`, `"linux"`, `"windows"`).
          - `"INSTALL_METHOD"` (`str`): The detected Python installation method (`"brew"`, `"system"`, `"standalone"`, `"microsoft_store"`).
          - `"EXTERNALLY_MANAGED"` (`bool`): Indicates whether the system restricts package installations.
          - `"BREW_AVAILABLE"` (`bool`): Specifies whether Homebrew is installed.

    ## Notes:
        - The function respects `EXTERNALLY-MANAGED` environments on Linux/macOS.
        - If Homebrew is available, it attempts to detect whether Python was installed via Brew.
        - Uses system commands like `dpkg -l`, `rpm -q`, and `ensurepip` to determine installation methods.
    """

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
    """
    Retrieve the installed version of a Homebrew-managed package.

    This function executes `brew list --versions <package>` to check whether a package
    is installed via Homebrew and extracts its version if available.

    ## Args:
        - `package` (`str`): The name of the package to check.

    ## Returns:
        - `Optional[str]`:
          - The installed version of the package if found.
          - `None` if the package is not installed via Homebrew.

    ## Notes:
        - Uses `subprocess.run()` to query Brew.
        - Returns `None` if the package is not installed.
    """

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
    """
    Retrieve the latest available version of a package from Homebrew.

    This function runs `brew info <package>` to extract the latest stable version
    of a package from the Homebrew repository.

    ## Args:
        - `package` (`str`): The name of the package to check.

    ## Returns:
        - `Optional[str]`:
          - The latest available version from Homebrew.
          - `None` if the package is unknown or Brew fails.

    ## Notes:
        - Parses the output of `brew info` to extract the stable version.
        - If the command fails or the package is not found, it returns `None`.
    """

    try:
        result = subprocess.run(
            [ "brew", "info", package ],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "stable" in line:
                return line.split()[1]  # Extract version
    except subprocess.CalledProcessError:
        return None  # Brew failed
