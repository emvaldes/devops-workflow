#!/usr/bin/env python3

# File: ./tests/conftest.py

__package__ = "tests"
__module__ = "conftest"

__version__ = "0.1.0"  # Updated Package version

# Standard library imports - Core system module
import sys
import os

# Standard library imports - Utility module
import json

# Standard library imports - File system-related module
from pathlib import Path

# Third-party library import - Testing framework
import pytest

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import system_params as params_utils

from mocks.config_loader import (
    load_mock_requirements,
    load_mock_installed
)

def get_base_config(
    package_name: str,
    module_name: str
) -> dict:

    validation_schema = {
        "requirements": [{}]  # Validate that the 'requirements' field is a list
    }

    # Determine the absolute path of the JSON file relative to this script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    REQUIREMENTS_FILEPATH = str(Path(SCRIPT_DIR) / "mocks" / "mock_requirements.json")

    BASE_CONFIG = params_utils.load_json_config(
        json_filepath=str(REQUIREMENTS_FILEPATH),
        validation_schema=validation_schema
    )
    # print(f'Base Config:\n{json.dumps(BASE_CONFIG, indent=4)}')

    # Ensure the required keys exist before replacing values
    BASE_CONFIG["logging"]["package_name"] = package_name
    BASE_CONFIG["logging"]["module_name"] = module_name
    BASE_CONFIG["logging"]["logs_dirname"] = f'logs/{package_name}'
    BASE_CONFIG["logging"]["log_filename"] = f'logs/{package_name}/{module_name}.log'

    # Convert installed.json path to Path object if present
    if "packages" in BASE_CONFIG and "installation" in BASE_CONFIG["packages"]:
        BASE_CONFIG["packages"]["installation"]["configs"] = Path(
            str(BASE_CONFIG["packages"]["installation"].get("configs", "packages/requirements/installed.json"))
        )
    # print(f'Config Data:\n{json.dumps(BASE_CONFIG, indent=4)}')

    return BASE_CONFIG

    # return {
    #     "colors": {},
    #     "logging": {
    #         "enable": True,
    #         "max_logfiles": 5,
    #         "package_name": package_name,
    #         "module_name": module_name,
    #         "logs_dirname": f"logs/{package_name}",
    #         "log_filename": f"logs/{package_name}/{module_name}.log"
    #     },
    #     "tracing": {
    #         "enable": False,
    #         "json": {"compressed": False}
    #     },
    #     "events": {},
    #     "stats": {},
    #     "requirements": [],
    #     "packages": {
    #         "installation": {
    #             "forced": False,
    #             "configs": Path("packages/requirements/installed.json")  # Ensure Path object
    #         }
    #     },
    #     "environment": {
    #         "OS": "",
    #         "INSTALL_METHOD": "",
    #         "EXTERNALLY_MANAGED": False,
    #         "BREW_AVAILABLE": False
    #     }
    # }

@pytest.fixture
def requirements_config(request) -> dict:

    package_name = getattr(
        request.module,
        "__package__",
        "unknown_package"
    )
    module_name = getattr(
        request.module,
        "__module__",
        "unknown_module"
    )

    base_config = get_base_config(
        package_name,
        module_name
    )
    mock_data = load_mock_requirements()

    # Merge mock data while ensuring required fields exist
    for key in base_config:
        base_config[key] = mock_data.get(
            key,
            base_config[key]
        )

    # Convert installed.json path to Path object
    base_config["packages"]["installation"]["configs"] = Path(
        base_config["packages"]["installation"]["configs"]
    )

    return base_config

@pytest.fixture
def installed_config(request) -> dict:

    package_name = getattr(
        request.module,
        "__package__",
        "unknown_package"
    )
    module_name = getattr(
        request.module,
        "__module__",
        "unknown_module"
    )

    base_config = get_base_config(
        package_name,
        module_name
    )
    mock_data = load_mock_installed()

    # Ensure installed packages are loaded correctly
    base_config["dependencies"] = mock_data.get(
        "dependencies", []
    )  # Keep `dependencies` instead of overriding `requirements`

    # Merge remaining mock data into base config
    for key in base_config:
        base_config[key] = mock_data.get(
            key,
            base_config[key]
        )

    # Convert installed.json path to Path object
    base_config["packages"]["installation"]["configs"] = Path(
        base_config["packages"]["installation"]["configs"]
    )

    return base_config

def main() -> None:
    pass

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
