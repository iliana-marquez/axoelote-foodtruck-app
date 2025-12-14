"""
Utility functions for booking system.
Reusable helpers for handling, calculating and formating.
1. Calculate duration between 2 datetimes (time formatting)
2. Determine what a customer can edit based on days until event.
"""
from .rules import FULL_EDIT_DAYS, COSMETIC_EDIT_DAYS, LOCKED_FIELDS, COSMETIC_FIELDS


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


def get_edit_permissions(booking):
    """
    Determine what a customer can edit based on days until event.

    Returns:
        dict: {
            'can_edit': bool,
            'edit_level': 'full' | 'cosmetic' | 'none',
            'days_until': int,
            'editable_fields': list,
            'locked_fields': list,
            'message': str
        }
    """
    if booking.status == 'cancelled':
        return {
            'can_edit': False,
            'edit_level': 'none',
            'days_until': None,
            'editable_fields': [],
            'locked_fields': [],
            'message': 'Cancelled bookings cannot be edited. Please create a new booking.'
        }

    days_until = (booking.start_datetime.date() - timezone.now().date()).days

    if days_until >= FULL_EDIT_DAYS:
        return {
            'can_edit': True,
            'edit_level': 'full',
            'days_until': days_until,
            'editable_fields': COSMETIC_FIELDS + LOCKED_FIELDS,
            'locked_fields': [],
            'message': 'You can edit all booking details.'
        }
    elif days_until >= COSMETIC_EDIT_DAYS:
        return {
            'can_edit': True,
            'edit_level': 'cosmetic',
            'days_until': days_until,
            'editable_fields': COSMETIC_FIELDS,
            'locked_fields': LOCKED_FIELDS,
            'message': f'Your event is in {days_until} days. Only title, description, and photo can be changed.'
        }
    else:
        return {
            'can_edit': False,
            'edit_level': 'none',
            'days_until': days_until,
            'editable_fields': [],
            'locked_fields': [],
            'message': f'Your event is in {days_until} days. Please contact us for urgent changes.'
        }
