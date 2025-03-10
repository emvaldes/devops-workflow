#!/usr/bin/env python3

# File: ./lib/manage_accesstoken.py
__version__ = "0.1.0"  ## Package version

import sys

from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# from lib import system_params
from lib.timezone_localoffset import get_local_offset
from lib.accesstoken_expiration import print_token_expiration
from lib.argument_parser import parse_arguments

def manage_accesstoken() -> None:

    # try:
    #     print_token_expiration( globals.DEBUG_MODE )
    #     get_local_offset( globals.DEBUG_MODE )
    # except Exception as e:
    #     print(
    #         f'An error occurred during token or timezone processing: {e}',
    #         file=sys.stderr
    #     )
    #     sys.exit(1)

    try:
        print_token_expiration(debug_mode)
        get_local_offset(debug_mode)
    except Exception as e:
        print(
            f'An error occurred during token or timezone processing: {e}',
            file=sys.stderr
        )
        sys.exit(1)

def main() -> None:

    # args = parse_arguments(
    #     context=["debug", "verbose"],
    #     description="Azure session and token expiration management."
    # )
    # # Update global flags
    # globals.DEBUG_MODE = args.debug
    # globals.VERBOSE_MODE = args.verbose
    # manage_accesstoken()

    args = parse_arguments(
        context=["debug", "verbose"],
        description="Azure session and token expiration management."
    )
    debug_mode = args.debug
    verbose_mode = args.verbose
    manage_accesstoken(debug_mode, verbose_mode)

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":
    main()
