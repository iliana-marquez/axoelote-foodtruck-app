"""
Business rules for booking system.
Centralized for easy adjustment and consistency.
"""

MINIMUM_ADVANCE_DAYS = 15  # Days before event that booking must be made
MINIMUM_GAP_HOURS = 10     # Hours required between events
MINIMUM_GUESTS = 70        # Minimum guest count per booking

# Edit permissions (days until event)
FULL_EDIT_DAYS = 15
COSMETIC_EDIT_DAYS = 3
NO_EDIT_DAYS = 2

# Field classifications
COSMETIC_FIELDS = ['event_title', 'description', 'event_photo']
LOCKED_FIELDS = [
    'start_datetime', 'end_datetime',
    'street_address', 'town_or_city', 'postcode', 'country',
    'guest_count', 'event_type', 'message'
]

# Contact information
CONTACT_EMAIL = 'booking@axoelote.com'
CONTACT_PHONE = '+43 123 456 78910'