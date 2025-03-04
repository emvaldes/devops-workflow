#!/usr/bin/env python3

# File: ./lib/timezone_localoffset.py
# Version: 0.1.0

"""
File: ./lib/timezone_localoffset.py

Description:
    Local Time Zone and Offset Manager
    This module retrieves and calculates the local time zone and its offset from UTC.
    It ensures accurate timekeeping and synchronization within the framework.

Core Features:
    - **Time Zone Detection**: Determines the local time zone using `pytz`.
    - **UTC Offset Calculation**: Computes the difference between local time and UTC.
    - **Command-Line Execution**: Provides CLI debugging for time zone information.

Usage:
    To retrieve and display the local time zone and offset:
    ```bash
    python timezone_localoffset.py --debug
    ```

Dependencies:
    - sys
    - pytz
    - datetime
    - argparse

Global Variables:
    - `LocalTimeZone` (pytz.timezone): Stores the detected local time zone.
    - `LocalOffset` (float): Stores the UTC offset of the local time zone in hours.

Exit Codes:
    - `0`: Successful execution.
    - `1`: Failure due to time zone retrieval errors.

Example:
    ```bash
    python timezone_localoffset.py --debug
    ```
"""

# Package version
__version__ = "0.1.0"

import sys
import pytz

from datetime import datetime
from pathlib import Path

# Ensure the current directory is added to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# from lib.argument_parser import parse_arguments

# Global variables for time zone and offset
LocalTimeZone = None
LocalOffset = None

def get_local_offset(
    debug: bool = False
) -> float:
    """
    Retrieves and calculates the local time zone offset from UTC.

    This function:
    - Determines the local time zone using `pytz`.
    - Computes the time difference (offset) between local time and UTC.
    - Prints local and UTC time information in a structured format.

    Args:
        debug (bool, optional): Enables additional debugging output. Defaults to False.

    Raises:
        Exception: If there is an error retrieving the time zone or calculating the offset.

    Returns:
        float: The UTC offset of the local time zone in hours.

    Workflow:
        1. Detects the system's local time zone using `pytz`.
        2. Retrieves the current local time and UTC time.
        3. Computes the time offset in hours.
        4. Prints formatted output for debugging if `debug` is enabled.

    Notes:
        - The default time zone is set to `"America/Creston"`, but it should be dynamically
          determined for broader applicability.
        - If an error occurs, it is printed to `stderr`, and the function exits with a failure code.
    """

    global LocalTimeZone, LocalOffset
    try:
        # Get the current local timezone using pytz
        local_tz = pytz.timezone( "America/Creston" )  # Customize this for the user's region if needed
        # Get aware local time and UTC time
        local_time = datetime.now( local_tz )  # local_time is now aware
        utc_time = datetime.now( pytz.utc )    # utc_time is aware as well
        # Calculate offset (difference between UTC and local time)
        local_offset = local_tz.utcoffset( local_time ).total_seconds() / 3600  # in hours
        LocalTimeZone = local_tz
        LocalOffset = local_offset
        # Print output in the requested format
        print(f'Local Time Zone:\t{local_tz} ({local_tz.utcoffset(local_time)})')
        print(f'Current Local Time:\t{local_time.strftime("%m/%d/%Y %H:%M:%S")}')
        print(f'Current UTC Time:\t{utc_time.strftime("%m/%d/%Y %H:%M:%S")}')
        print(f'Local Time Offset:\t{int(local_offset)} hours')
        # Debugging output if enabled
        if debug:
            print(f'\nLocal Time Zone:\t{local_tz} ({local_tz.tzname(local_time)})', file=sys.stdout)
            print(f'Current Local Time:\t{local_time.strftime("%m/%d/%Y %H:%M:%S")}', file=sys.stdout)
            print(f'Current UTC Time:\t{utc_time.strftime("%m/%d/%Y %H:%M:%S")}', file=sys.stdout)
            print(f'Local Time Offset:\t{local_offset} hours', file=sys.stdout)
        return local_offset
    except Exception as e:
        print(f'Error retrieving time zone: {e}', file=sys.stderr)

def main(
    debug: bool = False
) -> None:
    """
    Main entry point for processing time zone offset calculations.

    This function:
    - Calls `get_local_offset()` to retrieve the local time zone and UTC offset.
    - Handles exceptions that may arise during execution.

    Args:
        debug (bool, optional): Enables additional debugging output. Defaults to False.

    Raises:
        SystemExit: If an error occurs during time zone retrieval, the script exits with status `1`.

    Returns:
        None: This function does not return a value; it handles execution flow.

    Workflow:
        1. Calls `get_local_offset()` with the `debug` flag.
        2. Captures and logs any errors.
        3. Exits with a non-zero status code if an error occurs.

    Notes:
        - The function can be triggered via the command-line interface (CLI).
        - Debug mode prints additional details about the local time zone.
    """

    try:
        get_local_offset( debug )
    except Exception as e:
        print(f'Error processing time zone: {e}', file=sys.stderr)
        sys.exit( 1 )

if __name__ == "__main__":
    # Command-line argument parsing for debug and verbose
    parser = argparse.ArgumentParser(description="Retrieve and print local time zone and offset.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()
    # Set global flags based on user input
    debug = args.debug
    verbose = args.verbose
    main( debug=debug )
