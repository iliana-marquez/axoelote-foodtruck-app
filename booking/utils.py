"""
Utility functions for booking system.
Reusable helpers for calculating and formating.
"""


def calculate_duration(start_dt, end_dt):
    """
    Calculate duration between 2 datetimes

    Returns multiple formats:
    - total_minutes: int (for calculations)
    - total_hours: float (for calculations)
    - display: str (e.g., "Duration: 10h 30m" / for display)
    - display_compact: str (e.g., "10:30" / for display)
    """

    duration = end_dt - start_dt
    total_minutes = int(duration.total_seconds() // 60)
    total_hours = duration.total_seconds() / 3600

    hours = total_minutes // 60
    minutes = total_minutes % 60

    if minutes == 0:
        display = f"{hours}h"
    else:
        display = f"{hours}h {minutes}m"

    display_compact = f"{hours}:{minutes:02d}"

    return {
        'total_minutes': total_minutes,
        'total_hours': round(total_hours, 2),
        'display': display,
        'display_compact': display_compact
    }
