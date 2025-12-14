"""
Slot availability calculator for booking system.
Finds available time windows considering existing bookings and events.

Engagements = approved/pending Bookings or active Events

Slots can span across midnight for overnight bookings
(e.g. 20:00 - 02:00 next day).
"""

from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db.models import Q
from booking.models import Booking
from .rules import MINIMUM_GAP_HOURS
from .utils import calculate_duration
from events.models import Event


def get_engagements_for_date_range(start_date, end_date):
    """
    Get all enagements that could affect
    availability in date range

    Include engagements that:
    - Start within range, or
    - End within range (for multi-day events)

    Engagements include:
    - Bookings (pending or approved)
    - Events (active)
    """

    engagements = []

    # get pending or approved bookings
    bookings = Booking.objects.filter(
            status__in=['pending', 'approved']
        ).filter(
            Q(start_datetime__date__range=[start_date, end_date]) |
            Q(end_datetime__date__range=[start_date, end_date])
        ).values_list('start_datetime', 'end_datetime')

    for start, end in bookings:
        engagements.append({
            'start': start,
            'end': end
        })

    # get active events
    events = Event.objects.filter(
        status__in=['pending', 'approved']
        ).filter(
            Q(start_datetime__date__range=[start_date, end_date]) |
            Q(end_datetime__date__range=[start_date, end_date])
        ).values_list(
            'start_datetime',
            'end_datetime'
    )

    for start, end in events:
        engagements.append({
            'start': start,
            'end': end
        })

    return engagements


def get_available_slots(target_date, exclude_booking_id=None):
    """
    Calcualte available time slots that include target_date.
    Slots can extend overnight for overnight availability.

    Returns list of slots:
    [
        {'start': datetime, 'end': datetime, 'duration': {...}}
        ....
    ]

    Empty list means date is fully booked.
    """
    min_gap = timedelta(hours=MINIMUM_GAP_HOURS)

    # search window: day before through day after (3 days)
    search_start = timezone.make_aware(
        datetime.combine(target_date - timedelta(days=1), time(0, 0))
    )
    search_end = timezone.make_aware(
        datetime.combine(target_date + timedelta(days=2), time(0, 0))
    )

    # target_date boundaries for filtering relevant slots
    day_start = timezone.make_aware(
        datetime.combine(target_date, time(0, 0))
    )
    day_end = timezone.make_aware(
        datetime.combine(target_date + timedelta(days=1), time(0, 0))
    )

    # get all engagements in search window
    engagements = get_engagements_for_date_range(
        target_date - timedelta(days=1),
        target_date + timedelta(days=1)
    )

    # exclude current booking if editing
    if exclude_booking_id:
        booking = Booking.objects.filter(
                pk=exclude_booking_id
            ).values_list(
                'start_datetime',
                'end_datetime'
            ).first()
        if booking:
            engagements = [
                e for e in engagements
                if e['start'] != booking[0] or e['end'] != booking[1]
            ]

    # if no engagements, show full availability window
    if not engagements:
        duration = calculate_duration(day_start, day_end + timedelta(days=1))
        return [
            {
                'start': day_start,
                'end': day_end,
                'duration': duration
            }
        ]

    # sort engagements by start time
    engagements.sort(key=lambda x: x['start'])

    # calculate blocked periods (engagement time + gap on both sides)
    blocked_periods = []
    for engagement in engagements:
        block_start = engagement['start'] - min_gap
        block_end = engagement['end'] + min_gap
        blocked_periods.append(
            {
                'start': block_start,
                'end': block_end
            }
        )

    # merge overlapping blocked periods
    merged_blocks = []
    for block in blocked_periods:
        if merged_blocks and block['start'] <= merged_blocks[-1]['end']:
            # overlapping or adjacent extend the previous block
            merged_blocks[-1]['end'] = max(
                merged_blocks[-1]['end'], block['end']
                )
        else:
            merged_blocks.append(block.copy())

    # find available windows between blocked periods
    available_slots = []
    current_time = search_start

    for block in merged_blocks:
        slot_start = current_time
        slot_end = block['start']

        # only include slots that overlap with target date
        if slot_end > day_start and slot_end < day_end:
            duration = calculate_duration(slot_start, slot_end)

            # and extend over 1 hr min
            if duration['total_hours'] >= 1:
                available_slots.append({
                    'start': slot_start,
                    'end': slot_end,
                    'duration': duration
                })

        current_time = max(current_time, block['end'])

    # check reamaining time after last block
    if current_time < search_end:
        slot_start = current_time
        slot_end = search_end

        # only include if overlaps with target date
        if slot_end > day_start and slot_start < day_end:
            duration = calculate_duration(slot_start, slot_end)

            if duration['total_hours'] >= 1:
                available_slots.append({
                    'start': slot_start,
                    'end': slot_end,
                    'duration': duration
                })

    return available_slots


def format_slots_for_display(slots):
    """
    Format slots for template display.
    Shows date when slot crosses midnight.

    Returns:
    [
        {
            'start_date': '30 Jan 2026',
            'start_time': '20:00',
            'end_date': '31 Jan 2026',  # Only if different from start
            'end_time': '08:00',
            'duration': '12h',
            'duration_hours': 12.0,
            'crosses_midnight': True,
            'start_dt': datetime,
            'end_dt': datetime

        }
    ]
    """
    formatted_slots = []
    for slot in slots:
        crosses_midnight = slot['start'].date() != slot['end'].date()

        formatted_slots.append({
            'start_time': slot['start'].strftime('%H:%M'),
            'end_time': slot['end'].strftime('%H:%M'),
            'start_date': slot['start'].strftime('%d %b %Y'),
            'end_date': slot[
                'end'].strftime('%d %b %Y') if crosses_midnight else None,
            'duration': slot['duration']['display'],
            'duration_hours': slot['duration']['total_hours'],
            'crosses_midnight': crosses_midnight,
            'start_dt': slot['start'],
            'end_dt': slot['end'],
        })

    return formatted_slots


def check_slot_available(
        start_datetime,
        end_datetime,
        exclude_booking_id=None):
    """
    Safety net validation to check if a specific slot is available.
    Used as backend validation after usr selects slot.

    Args:
        start_datetime: datetime
        end_datetime: datetime
        exclude_booking_id: int (for editing existing bookings)
    """
    min_gap = timedelta(hours=MINIMUM_GAP_HOURS)

    # get engagements that could conflict
    engagements = get_engagements_for_date_range(
        start_datetime.date() - timedelta(days=1),
        end_datetime.date() + timedelta(days=1)
    )

    # exclude current booking if editing
    if exclude_booking_id:
        booking = Booking.objects.filter(
            pk=exclude_booking_id
        ).values_list(
            'start_datetime',
            'end_datetime'
        ).first()
        if booking:
            engagements = [
                e for e in engagements
                if e['start'] != booking[0] or e['end'] != booking[1]
            ]

    # check for concflicts
    for engagement in engagements:
        no_conflicts_before = end_datetime + min_gap <= engagement['start']
        no_conflicts_after = engagement['end'] + min_gap <= start_datetime

        if not (no_conflicts_before or no_conflicts_after):
            conflict_start = engagement['start'].strftime('%d.%m.%Y %H:%M')
            conflict_end = engagement['end'].strftime('%d.%m.%Y %H:%M')
            return (
                f"Conflicts with existing engagement ({conflict_start} - {conflict_end}). "
                f"Minimum {MINIMUM_GAP_HOURS}-hour gap required between bookings."
            )

    return None