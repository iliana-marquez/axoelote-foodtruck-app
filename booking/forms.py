
from .models import BookingRequest
from django.utils import timezone
from datetime import timedelta
from django import forms


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = [
            'event_title', 'event_type', 'guest_count',
            'start_datetime', 'end_datetime', 'description',
            'message', 'street_address', 'postcode', 
            'town_or_city', 'country', 'event_photo'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Event details (required for open events)'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Special requests, dietary restrictions, setup notes...'}),
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

        if start:
            min_booking_time = timezone.now() + timedelta(hours=72)
            if start < min_booking_time:
                raise forms.ValidationError("Events must be booked at least 72 hours (3 days) in advance.")
        
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")

        if event_type == 'open' and not description:
            raise forms.ValidationError("Description is required for open events.")

        return cleaned_data