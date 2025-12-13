from django.utils import timezone
from datetime import timedelta
from django import forms
from .models import Booking
from events.models import Event


MINIMUM_GAP_HOURS = 10  # Adjustable for iteration after trial


def check_time_conflicts(
        new_start,
        new_end,
        exclude_booking_id=None
        ):
    """
    Check for conflicts with existing Bookings and Events.
    Requires a minimum hour gap between events.
    Handles conflict scenarios with actionable suggestions.
    Returns error message if conflicts found, None otherwise.
    """
    min_gap = timedelta(hours=MINIMUM_GAP_HOURS)

    # collect all events to check for start/end times conflicts
    all_events = []

    # check Bookings
    bookings = Booking.objects.filter(
        status__in=[
            'pending',
            'approved'
        ]).values_list(
            'start_datetime',
            'end_datetime'
        )

    if exclude_booking_id:
        bookings = bookings.exclude(pk=exclude_booking_id)

    for start, end in bookings:
        all_events.append({
            'start': start,
            'end': end
        })

    # check Events
    events = Event.objects.filter(
            status='active'
        ).values_list(
            'start_datetime',
            'end_datetime'
        )

    for start, end in events:
        all_events.append({
            'start': start,
            'end': end
        })

    # categorise conflicts
    before_conflicts = []
    after_conflicts = []

    for event in all_events:
        no_conflict_before = new_end + min_gap <= event['start']
        no_conflict_after = event['end'] + min_gap <= new_start

        if not (no_conflict_before or no_conflict_after):
            if event['start'] < new_start:
                before_conflicts.append(event)
            else:
                after_conflicts.append(event)

    # no conflicts
    if not before_conflicts and not after_conflicts:
        return None

    # conflicts on start and end
    if before_conflicts and after_conflicts:
        latest_before_end = max(
            conflict['end'] for conflict in before_conflicts
        )
        earliest_after_start = min(
            conflict['start'] for conflict in after_conflicts
        )

        window_start = latest_before_end + min_gap
        window_end = earliest_after_start - min_gap
        window_duration = window_end - window_start

        if window_duration >= timedelta(hours=1):
            hours_available = int(window_duration.total_seconds() // 3600)

            window_start_str = window_start.strftime('%d %b %Y, %H:%M')

            if window_start.date() == window_end.date():
                window_end_str = window_end.strftime('%H:%M')
            else:
                window_end_str = window_end.strftime('%d %b %Y, %H:%M')

            return (
                f"Your booking conflicts w/existing events, "
                f"consider available window: "
                f"{window_start_str} till {window_end_str} / "
                f"{hours_available} hours available"
            )
        else:
            return (
                "This time slot is fully booked. "
                "Please choose a different date."
            )

    # only before conflicts, suggest starting later
    if before_conflicts:
        latest_end = max(
            conflict['end'] for conflict in before_conflicts
        )
        earliest_start = latest_end + min_gap
        earliest_start_str = earliest_start.strftime('%d %b %Y, %H:%M')

        return (
            "Your booking conflicts w/existing events, "
            f"try starting at {earliest_start_str} or later"
        )

    # only after conflicts, suggest ending earlier
    if after_conflicts:
        earliest_start = min(
            conflict['start'] for conflict in after_conflicts
        )
        latest_end = earliest_start - min_gap
        latest_end_str = latest_end.strftime('%d %b %Y, %H:%M')

        return (
            "Your booking conflicts w/existing events, "
            f"try ending by {latest_end_str} or earlier."
        )


class BookingRequestForm(forms.ModelForm):
    """
    Form for creating new booking requests
    """
    class Meta:
        model = Booking
        fields = [
            'event_title', 'event_type', 'guest_count',
            'start_datetime', 'end_datetime', 'description',
            'message', 'street_address', 'postcode',
            'town_or_city', 'country', 'event_photo'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local'
                       }),
            'end_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local'
                    }),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Event details (required for open events)'
                    }),
            'message': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Special requests,'
                    'dietary restrictions, setup notes...'
                    }),
            'event_photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        help_texts = {
            'message': 'DISCLAIMER: If no message is provided, no dietary considerations will be taken - food will be prepared according to our standard active menu.',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        event_type = cleaned_data.get('event_type')
        description = cleaned_data.get('description')

        # 15 day advance booking rule for new bookings
        if start:
            min_booking_time = timezone.now() + timedelta(days=15)
            if start < min_booking_time:
                raise forms.ValidationError(
                    "Events must be booked at least 15 days in advance."
                    )

        # validate inputs
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")

        if event_type == 'open' and not description:
            raise forms.ValidationError(
                "Description is required for open events."
                )

        # check for time conflicts
        if start and end:
            conflict_error = check_time_conflicts(start, end)
            if conflict_error:
                raise forms.ValidationError(conflict_error)

        return cleaned_data