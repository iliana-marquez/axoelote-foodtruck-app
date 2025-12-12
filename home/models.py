from django.db import models
from django_countries.fields import CountryField


# Create your models here.
class RegularSchedule(models.Model):
    venue_name = models.CharField(max_length=100, help_text="Location name (e.g., 'Naschmarkt')")
    street_address = models.CharField(max_length=80)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40)
    country = CountryField(blank_label="Select country", null=True, blank=True)

    # Days as individual boolean fields
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=False)

    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    # for checking specific weekdays
    def is_open_on_day(self, day_name):
        """Check if open on specific day"""
        return getattr(self, day_name.lower(), False)


def __str__(self):
    # Get list of active days
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_abbrevs = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    active_days = []
    for i, day in enumerate(days):
        if getattr(self, day):
            active_days.append(day_abbrevs[i])

    if not active_days:
        day_range = "Closed"
    elif len(active_days) == 1:
        day_range = active_days[0]
    else:
        # Check if days are consecutive
        day_indices = [i for i, day in enumerate(days) if getattr(self, day)]
        consecutive = all(day_indices[i] + 1 == day_indices[i + 1] for i in range(len(day_indices) - 1))

        if consecutive:
            day_range = f"{active_days[0]} - {active_days[-1]}"
        else:
            # Non-consecutive days, show all
            day_range = ", ".join(active_days)

    return f"{self.venue_name} - {day_range} {self.opening_time} to {self.closing_time}"