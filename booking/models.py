from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator


EVENT_TYPES = [
    ('open', 'Open Event'),
    ('private', 'Private Event'),
]
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


# Create your models here.
class BookingRequest(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="booking_requests"
    )
    event_title = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    guest_count = models.PositiveIntegerField(
        validators=[MinValueValidator(70)]
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True, help_text="Event details (for open events)")
    message = models.TextField(blank=True, help_text="Special requests, dietary restrictions, setup notes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    street_address = models.CharField(max_length=80, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_or_city = models.CharField(max_length=40, null=True, blank=True)
    country = CountryField(blank_label="Select country", null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_photo = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"{self.created_at.strftime('%m/%d/%Y %H:%M')} - {self.customer.username} | {self.event_title} - {self.start_datetime.strftime('%m/%d/%Y %H:%M')} ({self.get_status_display()})"