#!/usr/bin/env python3

# File: ./tests/test_conftest.py

__package__ = "tests"
__module__ = "test_conftest"

__version__ = "0.1.0"  ## Test Module version

# Standard library imports - Core system module
import sys
import subprocess
import json

# Standard library imports - File system-related module
from pathlib import Path

# Standard library imports - Unit testing and mocking tools
from unittest.mock import (
    ANY,
    patch,
    mock_open
)

# Third-party library imports - Testing framework
import pytest

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tests.mocks.config_loader import load_mock_requirements, load_mock_installed
from tests.conftest import get_base_config

def test_get_base_config():

    package_name = "test_package"
    module_name = "test_module"
    config = get_base_config(package_name, module_name)

    assert config["logging"]["package_name"] == package_name
    assert config["logging"]["module_name"] == module_name
    assert isinstance(config["packages"]["installation"]["configs"], Path)

def test_requirements_config(requirements_config):

    assert "logging" in requirements_config
    assert "requirements" in requirements_config
    assert isinstance(requirements_config["requirements"], list)
    assert len(requirements_config["requirements"]) > 0

def test_installed_config(installed_config):

    assert "dependencies" in installed_config
    assert isinstance(installed_config["dependencies"], list)

def test_requirements_config_path_type(requirements_config):

    assert isinstance(requirements_config["packages"]["installation"]["configs"], Path)

def test_installed_config_path_type(installed_config):

    assert isinstance(installed_config["packages"]["installation"]["configs"], Path)

def main() -> None:
    pass

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
