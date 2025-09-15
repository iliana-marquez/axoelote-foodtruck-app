from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError


EVENT_TYPES = [
    ('open', 'Open Event'),        # Public events shown to customers
    ('private', 'Private Event'),  # Private bookings, limited public info
    ('closure', 'Closure'),        # Day off, maintenance, etc.
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('postponed', 'Postponed'),   # Future feature: automatic customer notifications
    ('cancelled', 'Cancelled'),
]


class Event(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_events'
    )
    event_title = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    street_address = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, blank=True)
    country = CountryField(blank_label="Select country", null=True, blank=True)
    description = models.TextField()
    message = models.TextField(
        blank=True,
        help_text="Internal notes: vendor contacts, setup requirements, etc."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    event_photo = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.event_type in ['open', 'private']:
            if not self.street_address:
                raise ValidationError("Street address is required for open and private events.")
            if not self.town_or_city:
                raise ValidationError("Town/city is required for open and private events.")

        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.admin.username} - {self.start_datetime.strftime('%m/%d/%Y %H:%M')}"

    class Meta:
        ordering = ['start_datetime']
