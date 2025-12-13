from django.utils import timezone
from datetime import timedelta
from django import forms
from .models import Booking
from .rules import MINIMUM_ADVANCE_DAYS
from .slots import check_slot_available


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
            'message': 'DISCLAIMER: If no message is provided, '
            'no dietary considerations will be taken - '
            'food will be prepared according to our standard active menu.',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        event_type = cleaned_data.get('event_type')
        description = cleaned_data.get('description')

        # Check for past dates
        if start and start.date() < timezone.now().date():
            raise forms.ValidationError(
                "Cannot book dates in the past."
            )

        # Advance booking rule
        if start:
            min_booking_time = timezone.now() + timedelta(
                days=MINIMUM_ADVANCE_DAYS)
            if start < min_booking_time:
                raise forms.ValidationError(
                    f"Events must be booked at least {
                        MINIMUM_ADVANCE_DAYS
                        } days in advance."
                    )

        # check end is after start
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")

        # open events require description for ui display
        if event_type == 'open' and not description:
            raise forms.ValidationError(
                "Description is required for open events."
                )

        # check for time conflicts
        if start and end:
            conflict_error = check_slot_available(start, end)
            if conflict_error:
                raise forms.ValidationError(conflict_error)

        return cleaned_data