#!/usr/bin/env python3

# Python File: ./lib/timezone_localoffset.py
__version__ = "0.1.0"  # Documentation version

MODULE_DOCSTRING = """
Overview:
    The `timezone_localoffset.py` module is responsible for retrieving and computing
the local time zone and its offset from UTC. This module ensures accurate timekeeping
and synchronization within the framework.

Core Features:
    - Detects the local time zone using `pytz`.
    - Computes the time difference (offset) between local time and UTC.
    - Provides CLI debugging capabilities for time zone verification.

Expected Behavior & Usage:
    Retrieving and displaying the local time zone and offset:
        python timezone_localoffset.py --debug

    Programmatically obtaining the local offset:
        from lib.timezone_localoffset import get_local_offset
        offset = get_local_offset()
"""

FUNCTION_DOCSTRINGS = {
    "get_local_offset": """
    Retrieves and calculates the local time zone offset from UTC.

    Parameters:
        debug (bool, optional): Enables additional debugging output. Defaults to False.

    Returns:
        float: The UTC offset of the local time zone in hours.

    Behavior:
        - Detects the system's local time zone using `pytz`.
        - Retrieves the current local time and UTC time.
        - Computes the time offset in hours.
        - Prints formatted output for debugging if `debug` is enabled.

    Notes:
        - The default time zone is set to "America/Creston" but should be dynamically determined.
        - If an error occurs, the function prints the error and exits with a failure code.
    """,
    "main": """
    Main execution function that processes time zone offset calculations.

    Parameters:
        debug (bool, optional): Enables additional debugging output. Defaults to False.

    Returns:
        None: Handles execution flow without returning a value.

    Behavior:
        - Calls `get_local_offset()` to retrieve the local time zone and UTC offset.
        - Captures and logs any errors that occur during execution.
        - Exits with a non-zero status code if an error occurs.
    """
}

VARIABLE_DOCSTRINGS = {
    "LocalTimeZone": "Stores the detected local time zone as a `pytz.timezone` object.",
    "LocalOffset": "Stores the computed UTC offset of the local time zone in hours."
}
