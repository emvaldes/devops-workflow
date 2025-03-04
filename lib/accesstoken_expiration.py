#!/usr/bin/env python3

# File: ./lib/accesstoken_expiration.py
# Version: 0.1.0

"""
File: ./lib/accesstoken_expiration.py

Description:
    Azure Access Token Expiration Manager
    This module retrieves and manages Azure access tokens. It utilizes the `azure.identity`
    package to fetch tokens and determine their expiration details.

Features:
    - **Fetches Azure Access Tokens**: Uses `InteractiveBrowserCredential` to obtain an access token.
    - **Token Expiration Tracking**: Determines and prints the expiration time of the retrieved token.
    - **Time Remaining Calculation**: Computes and displays the remaining time before the token expires.
    - **Command-Line Interface**: Supports debugging options for token validity and expiration tracking.

Usage:
    Run this script to retrieve an Azure access token and check its expiration details:
    ```bash
    python accesstoken_expiration.py --debug
    ```

Dependencies:
    - azure-identity
    - azure-core

Global Variables:
    - `TokenScope` (str): The scope URL for requesting Azure management API tokens.
    - `AccessToken` (str | None): Stores the currently fetched access token.
    - `TokenExpiration` (datetime | None): Stores the expiration timestamp of the current token.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to errors in token retrieval or expiration calculation.

Example:
    ```bash
    python accesstoken_expiration.py --debug
    ```
"""

# Package version
__version__ = "0.1.0"

import sys

from typing import Optional
from datetime import datetime
from azure.identity import InteractiveBrowserCredential
from azure.core.exceptions import AzureError

# Global variables
TokenScope = "https://management.azure.com/"
AccessToken = None
TokenExpiration = None

def get_access_token() -> Optional[datetime]:
    """
    Retrieves an Azure access token and extracts its expiration time.

    Returns:
        datetime | None:
            - The expiration datetime of the retrieved Azure access token.
            - Returns None if an error occurs during token retrieval.

    Raises:
        AzureError: If authentication fails while fetching the token.
        Exception: If an unexpected error occurs during the process.

    Process:
        1. Uses `InteractiveBrowserCredential()` to authenticate and fetch an access token.
        2. Extracts the token expiration timestamp from the response.
        3. Converts the expiration timestamp to a `datetime` object.
        4. Stores the token globally for further use.

    Notes:
        - This function uses global storage (`AccessToken`) for token persistence.
        - If authentication fails, the function logs an error and returns None.
    """

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
    """
    Retrieves and prints the Azure access token expiration time.

    Args:
        debug (bool, optional): If True, prints the access token details for debugging. Defaults to False.

    Returns:
        datetime | None:
            - The expiration datetime of the access token.
            - Returns None if the token cannot be retrieved.

    Raises:
        Exception: If an error occurs while retrieving or formatting the expiration time.

    Workflow:
        1. Calls `get_access_token()` to retrieve the token and its expiration time.
        2. If successful, stores the expiration timestamp globally (`TokenExpiration`).
        3. Optionally prints the full token JSON if `debug` mode is enabled.
        4. Converts the expiration time to a human-readable format and displays it.

    Notes:
        - If the token cannot be retrieved, an error message is logged, and the function returns None.
        - This function does not modify the token validity but only reports its status.
    """

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
    """
    Calculates and prints the remaining time before the Azure access token expires.

    Returns:
        None: This function does not return any values; it prints the remaining time instead.

    Raises:
        Exception: If an error occurs while computing the remaining time.

    Calculation Process:
        1. Checks if `TokenExpiration` is set.
        2. Computes the time difference between the current time and expiration time.
        3. Converts the time difference into hours, minutes, and seconds.
        4. Prints the remaining time in a human-readable format.

    Notes:
        - If `TokenExpiration` is not set, the function logs an error message and exits.
        - This function does not modify or renew the token; it only reports its expiration status.
    """

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
    """
    Main entry point to retrieve and manage Azure access token expiration.

    Args:
        debug (bool, optional): If True, enables detailed logging of token retrieval. Defaults to False.

    Returns:
        None: This function does not return values; it coordinates the retrieval and reporting processes.

    Raises:
        Exception: If a critical error occurs during execution.

    Workflow:
        1. Calls `print_token_expiration()` to retrieve and display the token's expiration time.
        2. Calls `print_remaining_time()` to calculate and display the remaining validity time.

    Notes:
        - If an error occurs, an appropriate message is logged, and execution is halted.
        - This function does not refresh tokens; it only reports existing credentials.
    """

    try:
        print_token_expiration( debug=debug )
        print_remaining_time()
    except Exception as e:
        print(
            f'Critical error: {e}',
            file=sys.stderr
        )
        sys.exit(1)

if __name__ == "__main__":
    from argument_parser import parse_arguments
    args = parse_arguments(
        context=["debug", "verbose"],
        description="Manage Azure access token expiration."
    )
    main( debug=args.debug )
