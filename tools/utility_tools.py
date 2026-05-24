"""
tools/utility_tools.py
-----------------------
PURPOSE: General-purpose utility tools that are not domain-specific.
"""

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_date_and_time() -> str:
    """
    Get the current date and time.

    Use this tool when the user's question involves "today", "now",
    or relative time references.

    Returns:
        Current date and time as a formatted string.
    """
    now = datetime.now()
    return (
        f"Current Date & Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        f"Day of Year: {now.timetuple().tm_yday}/365\n"
        f"Year Progress: {(now.timetuple().tm_yday / 365 * 100):.1f}%\n"
    )
