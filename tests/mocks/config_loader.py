#!/usr/bin/env python3

# File: ./tests/mocks/config_loader.py

__package__ = "tests.mocks"
__module__ = "config_loader"

__version__ = "0.1.0"  # Module version

# Standard library imports - Core system module
import sys
import json

# Standard library imports - File system-related module
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

MOCKS_DIR = Path(__file__).resolve().parent  # `tests/mocks/`

# ✅ Base structure for `mock_requirements.json` (policy settings)
BASE_REQUIREMENTS_CONFIG = {
    "colors": {},
    "logging": {
        "enable": True,
        "max_logfiles": 5,
        "package_name": "<package-name>",
        "module_name": "<module-name>",
        "logs_dirname": "logs/<package-name>",
        "log_filename": "logs/<package-name>/<module-name>.log"
    },
    "tracing": {
        "enable": False,
        "json": {
            "compressed": False
        }
    },
    "events": {},
    "stats": {},
    "requirements": [],
    "packages": {
        "installation": {
            "forced": False,
            "configs": "packages/requirements/installed.json"
        }
    },
    "environment": {
        "OS": "",
        "INSTALL_METHOD": "",
        "EXTERNALLY_MANAGED": False,
        "BREW_AVAILABLE": False
    }
}

# ✅ Base structure for `mock_installed.json` (installed packages)
BASE_INSTALLED_CONFIG = {
    "colors": BASE_REQUIREMENTS_CONFIG["colors"],
    "logging": BASE_REQUIREMENTS_CONFIG["logging"],
    "tracing": BASE_REQUIREMENTS_CONFIG["tracing"],
    "events": BASE_REQUIREMENTS_CONFIG["events"],
    "stats": BASE_REQUIREMENTS_CONFIG["stats"],
    "requirements": [],
    "packages": BASE_REQUIREMENTS_CONFIG["packages"],
    "environment": BASE_REQUIREMENTS_CONFIG["environment"]
}

def load_mock_requirements() -> dict:
    """Load and return the contents of `mock_requirements.json`, ensuring missing fields are populated."""
    file_path = MOCKS_DIR / "mock_requirements.json"
    if not file_path.exists():
        return BASE_REQUIREMENTS_CONFIG  # ✅ Return base config if file is missing

    with open(file_path, "r") as file:
        data = json.load(file)

    # ✅ Ensure base structure is maintained
    for key in BASE_REQUIREMENTS_CONFIG:
        data.setdefault(key, BASE_REQUIREMENTS_CONFIG[key])

    return data

def load_mock_installed() -> dict:
    """Load and return the contents of `mock_installed.json`, ensuring missing fields are populated."""
    file_path = MOCKS_DIR / "mock_installed.json"
    if not file_path.exists():
        return BASE_INSTALLED_CONFIG  # ✅ Return base config if file is missing

    with open(file_path, "r") as file:
        data = json.load(file)

    # ✅ Ensure base structure is maintained
    for key in BASE_INSTALLED_CONFIG:
        data.setdefault(key, BASE_INSTALLED_CONFIG[key])

    return data

def main() -> None:
    pass

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
