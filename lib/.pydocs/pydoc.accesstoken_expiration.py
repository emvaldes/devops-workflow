#!/usr/bin/env python3

# Python File: ./lib/accesstoken_expiration.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
Overview
    The `accesstoken_expiration.py` module manages Azure access tokens, retrieving expiration times and displaying the remaining validity duration.

Core Features:
    - Fetches an Azure access token using `InteractiveBrowserCredential`.
    - Extracts and displays token expiration information.
    - Provides a function to check the remaining time before expiration.
    - Handles Azure authentication errors gracefully.

Expected Behavior & Usage:
    Retrieving Token Expiration:
        from lib.accesstoken_expiration import print_token_expiration
        expiration = print_token_expiration(debug=True)

    Checking Remaining Validity:
        from lib.accesstoken_expiration import print_remaining_time
        print_remaining_time()
"""

FUNCTION_DOCSTRINGS = {
    "get_access_token": """
    Retrieves an Azure access token and determines its expiration time.

    Returns:
        Optional[datetime]: The expiration time of the access token, or None if retrieval fails.
""",
    "print_token_expiration": """
    Fetches and prints the access token expiration time.

    Parameters:
        debug (bool, optional): Enables debug logging of token details. Defaults to False.

    Returns:
        Optional[datetime]: The token expiration timestamp or None if unavailable.
""",
    "print_remaining_time": """
    Computes and prints the remaining validity duration of the access token.

    Displays:
        - Hours, minutes, and seconds left before expiration.
        - An error message if expiration is not available.
""",
    "main": """
    Entry point function that executes the token retrieval and expiration checks.

    Parameters:
        debug (bool, optional): Enables debugging mode. Defaults to False.
"""
}

VARIABLE_DOCSTRINGS = {
    "TokenScope": "The scope used for Azure authentication requests.",
    "AccessToken": "Holds the retrieved access token. Defaults to None until fetched.",
    "TokenExpiration": "Stores the expiration timestamp of the retrieved access token."
}
