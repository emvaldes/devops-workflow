#!/usr/bin/env python3

# File: ./lib/accesstoken_expiration.py
__version__ = "0.1.0"  ## Package version

# Standard library imports - Core system modules
import sys

# Standard library imports - Date and file handling modules
from datetime import datetime
from pathlib import Path

# Standard library imports - Type hinting (kept in a separate group)
from typing import Optional

# Third-party library imports - Azure SDK modules
from azure.core.exceptions import AzureError
from azure.identity import InteractiveBrowserCredential

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Global variables
TokenScope = "https://management.azure.com/"
AccessToken = None
TokenExpiration = None

def get_access_token() -> Optional[datetime]:

    global AccessToken
    try:
        credential = InteractiveBrowserCredential()
        token = credential.get_token( "https://management.azure.com/.default" )
        AccessToken = token.token  # Storing the access token globally
        return datetime.datetime.utcfromtimestamp( token.expires_on )  # Expiration time
    except AzureError as e:
        print(
            f'Azure SDK error while fetching token: {e}',
            file=sys.stderr
        )
        return None
    except Exception as e:
        print(
            f'Error fetching access token: {e}',
            file=sys.stderr
        )
        return None

def print_token_expiration(
    debug: bool = False
) -> Optional[datetime]:

    global TokenExpiration
    try:
        # Fetch the token and its expiration
        token_expiration = get_access_token()
        if not token_expiration:
            print(
                "Failed to retrieve or parse the access token.",
                file=sys.stderr
            )
            return
        # Set the expiration globally
        TokenExpiration = token_expiration
        # Debugging output if enabled
        if debug:
            print(
                f'Access Token (JSON) -> {{"accessToken": "{AccessToken}", "expiresOn": "{TokenExpiration}"}}',
                file=sys.stdout
            )
        # Handle the expiration
        if not TokenExpiration:
            print(
                "Token expiration not found.",
                file=sys.stderr
            )
            return
        # Convert to time string
        expiration_string = TokenExpiration.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if not expiration_string:
            print(
                "Token expiration string is empty.",
                file=sys.stderr
            )
            return
        print(
            f'Token expiration date: {expiration_string}',
            file=sys.stdout
        )
        return TokenExpiration
    except Exception as e:
        print(
            f'Error processing token expiration: {e}',
            file=sys.stderr
        )

def print_remaining_time() -> None:

    try:
        if TokenExpiration:
            current_time = datetime.datetime.now()
            time_remaining = TokenExpiration - current_time
            hours_remaining = time_remaining.total_seconds() // 3600
            minutes_remaining = (time_remaining.total_seconds() % 3600) // 60
            seconds_remaining = time_remaining.total_seconds() % 60
            print(
                f'Available Remaining Time: {int(hours_remaining)} hours, {int(minutes_remaining)} minutes, {int(seconds_remaining)} seconds',
                file=sys.stdout
            )
        else:
            print(
                "Token expiration is not set, unable to calculate remaining time.",
                file=sys.stderr
            )
    except Exception as e:
        print(
            f'Error calculating remaining time: {e}',
            file=sys.stderr
        )

def main(
    debug: bool = False
) -> None:

    try:
        print_token_expiration( debug=debug )
        print_remaining_time()
    except Exception as e:
        print(
            f'Critical error: {e}',
            file=sys.stderr
        )
        sys.exit(1)

# Load documentation dynamically and apply module, function and objects docstrings
from lib.pydoc_loader import load_pydocs
load_pydocs(__file__, sys.modules[__name__])

if __name__ == "__main__":

    from argument_parser import parse_arguments
    args = parse_arguments(
        context=["debug", "verbose"],
        description="Manage Azure access token expiration."
    )

    main( debug=args.debug )
