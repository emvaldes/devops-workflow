#!/usr/bin/env python3

# File: ./tests/conftest.py

__package__ = "tests"
__module__ = "conftest"

__version__ = "0.1.0"  # Updated Package version

# Standard library imports - Core system module
import sys

# Standard library imports - File system-related module
from pathlib import Path

# Third-party library import - Testing framework
import pytest

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mocks.config_loader import (
    load_mock_requirements,
    load_mock_installed
)

def get_base_config(
    package_name: str,
    module_name: str
) -> dict:

    return {
        "colors": {},
        "logging": {
            "enable": True,
            "max_logfiles": 5,
            "package_name": package_name,
            "module_name": module_name,
            "logs_dirname": f"logs/{package_name}",
            "log_filename": f"logs/{package_name}/{module_name}.log"
        },
        "tracing": {
            "enable": False,
            "json": {"compressed": False}
        },
        "events": {},
        "stats": {},
        "requirements": [],
        "packages": {
            "installation": {
                "forced": False,
                "configs": Path("packages/requirements/installed.json")  # Ensure Path object
            }
        },
        "environment": {
            "OS": "",
            "INSTALL_METHOD": "",
            "EXTERNALLY_MANAGED": False,
            "BREW_AVAILABLE": False
        }
    }

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
