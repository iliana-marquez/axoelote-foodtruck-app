# booking/test_slots.py
"""
Automated tests for slots.py
Run with: python manage.py test booking.test_slots -v 2
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, time, datetime
from .slots import (
    get_available_slots,
    get_engagements_for_date_range,
    format_slots_for_display,
    check_slot_available
)
from .utils import calculate_duration
from .models import Booking
from events.models import Event


class CalculateDurationTest(TestCase):
    """Tests for calculate_duration utility function."""

    def test_whole_hours(self):
        """Test duration with whole hours."""
        start = timezone.now()
        end = start + timedelta(hours=5)
        result = calculate_duration(start, end)

        self.assertEqual(result['total_minutes'], 300)
        self.assertEqual(result['total_hours'], 5.0)
        self.assertEqual(result['display'], '5h')
        self.assertEqual(result['display_compact'], '5:00')

    def test_hours_and_minutes(self):
        """Test duration with hours and minutes."""
        start = timezone.now()
        end = start + timedelta(hours=10, minutes=30)
        result = calculate_duration(start, end)

        self.assertEqual(result['total_minutes'], 630)
        self.assertEqual(result['total_hours'], 10.5)
        self.assertEqual(result['display'], '10h 30m')
        self.assertEqual(result['display_compact'], '10:30')

    def test_minutes_only(self):
        """Test duration less than one hour."""
        start = timezone.now()
        end = start + timedelta(minutes=45)
        result = calculate_duration(start, end)

        self.assertEqual(result['total_minutes'], 45)
        self.assertEqual(result['total_hours'], 0.75)
        self.assertEqual(result['display'], '0h 45m')
        self.assertEqual(result['display_compact'], '0:45')


class GetEngagementsTest(TestCase):
    """Tests for get_engagements_for_date_range function."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_no_engagements(self):
        """Empty database returns empty list."""
        target = date(2026, 3, 15)
        engagements = get_engagements_for_date_range(
            target - timedelta(days=1),
            target + timedelta(days=1)
        )
        self.assertEqual(engagements, [])

    def test_finds_booking_in_range(self):
        """Finds booking that starts in range."""
        start_dt = timezone.make_aware(datetime(2026, 3, 15, 10, 0))
        end_dt = timezone.make_aware(datetime(2026, 3, 15, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Test Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        engagements = get_engagements_for_date_range(
            date(2026, 3, 14),
            date(2026, 3, 16)
        )

        self.assertEqual(len(engagements), 1)
        self.assertEqual(engagements[0]['start'], start_dt)
        self.assertEqual(engagements[0]['end'], end_dt)

    def test_ignores_cancelled_booking(self):
        """Cancelled bookings not included."""
        start_dt = timezone.make_aware(datetime(2026, 3, 15, 10, 0))
        end_dt = timezone.make_aware(datetime(2026, 3, 15, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Cancelled Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='cancelled',
            street_address='123 Test St',
            postcode='12345'
        )

        engagements = get_engagements_for_date_range(
            date(2026, 3, 14),
            date(2026, 3, 16)
        )

        self.assertEqual(engagements, [])

    def test_ignores_rejected_booking(self):
        """Rejected bookings not included."""
        start_dt = timezone.make_aware(datetime(2026, 3, 15, 10, 0))
        end_dt = timezone.make_aware(datetime(2026, 3, 15, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Rejected Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='rejected',
            street_address='123 Test St',
            postcode='12345'
        )

        engagements = get_engagements_for_date_range(
            date(2026, 3, 14),
            date(2026, 3, 16)
        )

        self.assertEqual(engagements, [])

    def test_finds_multi_day_booking_by_end_date(self):
        """Finds booking that ends in range but starts before."""
        start_dt = timezone.make_aware(datetime(2026, 3, 13, 20, 0))
        end_dt = timezone.make_aware(datetime(2026, 3, 15, 2, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Multi-day Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        engagements = get_engagements_for_date_range(
            date(2026, 3, 14),
            date(2026, 3, 16)
        )

        self.assertEqual(len(engagements), 1)


class GetAvailableSlotsTest(TestCase):
    """Tests for get_available_slots function."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_empty_day_returns_48_hours(self):
        """No engagements returns 48 hour window."""
        target = date(2026, 4, 15)
        slots = get_available_slots(target)

        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]['duration']['total_hours'], 48)

    def test_single_midday_engagement_blocks_full_day(self):
        """
        Mid-day engagement with 10hr gap blocks entire day.
        This is expected behavior - ensures owner has proper rest
        between late-night and next-day events.
        """
        target = date(2026, 4, 20)

        # 10:00-14:00 engagement
        # Block: 00:00 (10:00-10hr) to 00:00 next day (14:00+10hr)
        start_dt = timezone.make_aware(datetime(2026, 4, 20, 10, 0))
        end_dt = timezone.make_aware(datetime(2026, 4, 20, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Mid-day Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        slots = get_available_slots(target)

        # Full day blocked - expected with 10hr gap rule
        self.assertEqual(slots, [])

    def test_single_engagement_creates_slot_after(self):
        """Early engagement leaves slot available later in day."""
        target = date(2026, 4, 20)

        # Create engagement 02:00-04:00
        # Block: 16:00 day before to 14:00 target day
        # Leaves: 14:00 onwards available
        start_dt = timezone.make_aware(datetime(2026, 4, 20, 2, 0))
        end_dt = timezone.make_aware(datetime(2026, 4, 20, 4, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Early Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        slots = get_available_slots(target)

        # Should have slot starting at 14:00 (04:00 + 10hr gap)
        self.assertGreaterEqual(len(slots), 1)

    def test_fully_booked_returns_empty(self):
        """Multiple engagements that fill day returns empty list."""
        target = date(2026, 4, 25)

        # Create engagement that blocks entire day with gaps
        # 00:00-04:00 blocks until 14:00 (04:00 + 10hr)
        start_dt1 = timezone.make_aware(datetime(2026, 4, 25, 0, 0))
        end_dt1 = timezone.make_aware(datetime(2026, 4, 25, 4, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Early Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt1,
            end_datetime=end_dt1,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        # 14:00-18:00 blocks from 04:00 (14:00 - 10hr) to 04:00 next day (18:00 + 10hr)
        start_dt2 = timezone.make_aware(datetime(2026, 4, 25, 14, 0))
        end_dt2 = timezone.make_aware(datetime(2026, 4, 25, 18, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Afternoon Event',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt2,
            end_datetime=end_dt2,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        slots = get_available_slots(target)

        # With 10hr gaps, these two events should leave no room
        self.assertEqual(slots, [])

    def test_exclude_booking_id(self):
        """Excluding booking ID allows slot in its time."""
        target = date(2026, 4, 30)

        start_dt = timezone.make_aware(datetime(2026, 4, 30, 10, 0))
        end_dt = timezone.make_aware(datetime(2026, 4, 30, 14, 0))

        booking = Booking.objects.create(
            customer=self.user,
            event_title='My Booking',
            event_type='private',
            guest_count=80,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        # Without exclude - booking blocks time
        slots_blocked = get_available_slots(target)

        # With exclude - booking's slot available
        slots_available = get_available_slots(target, exclude_booking_id=booking.pk)

        # Should have more availability when excluding
        self.assertGreater(
            slots_available[0]['duration']['total_hours'] if slots_available else 0,
            slots_blocked[0]['duration']['total_hours'] if slots_blocked else 0
        )


class CheckSlotAvailableTest(TestCase):
    """Tests for check_slot_available safety function."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_available_slot_returns_none(self):
        """Available slot returns None (no error)."""
        start = timezone.make_aware(datetime(2026, 5, 15, 10, 0))
        end = timezone.make_aware(datetime(2026, 5, 15, 14, 0))

        result = check_slot_available(start, end)

        self.assertIsNone(result)

    def test_conflict_returns_error_message(self):
        """Conflicting slot returns error string."""
        # Create existing booking
        existing_start = timezone.make_aware(datetime(2026, 5, 20, 10, 0))
        existing_end = timezone.make_aware(datetime(2026, 5, 20, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Existing Event',
            event_type='private',
            guest_count=80,
            start_datetime=existing_start,
            end_datetime=existing_end,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        # Try to book overlapping time (within 10hr gap)
        new_start = timezone.make_aware(datetime(2026, 5, 20, 16, 0))
        new_end = timezone.make_aware(datetime(2026, 5, 20, 20, 0))

        result = check_slot_available(new_start, new_end)

        self.assertIsNotNone(result)
        self.assertIn("no longer available", result)

    def test_10_hour_gap_respected(self):
        """Booking with exactly 10hr gap is allowed."""
        # Create existing booking 10:00-14:00
        existing_start = timezone.make_aware(datetime(2026, 5, 25, 10, 0))
        existing_end = timezone.make_aware(datetime(2026, 5, 25, 14, 0))

        Booking.objects.create(
            customer=self.user,
            event_title='Existing Event',
            event_type='private',
            guest_count=80,
            start_datetime=existing_start,
            end_datetime=existing_end,
            status='approved',
            street_address='123 Test St',
            postcode='12345'
        )

        # Book starting exactly 10hrs after (00:00 next day)
        new_start = timezone.make_aware(datetime(2026, 5, 26, 0, 0))
        new_end = timezone.make_aware(datetime(2026, 5, 26, 4, 0))

        result = check_slot_available(new_start, new_end)

        self.assertIsNone(result)


class FormatSlotsForDisplayTest(TestCase):
    """Tests for format_slots_for_display function."""

    def test_same_day_slot(self):
        """Slot within same day formats correctly."""
        start = timezone.make_aware(datetime(2026, 6, 15, 10, 0))
        end = timezone.make_aware(datetime(2026, 6, 15, 14, 0))

        slots = [{
            'start': start,
            'end': end,
            'duration': calculate_duration(start, end)
        }]

        formatted = format_slots_for_display(slots)

        self.assertEqual(formatted[0]['start_time'], '10:00')
        self.assertEqual(formatted[0]['end_time'], '14:00')
        self.assertEqual(formatted[0]['start_date'], '15 Jun 2026')
        self.assertIsNone(formatted[0]['end_date'])
        self.assertFalse(formatted[0]['crosses_midnight'])

    def test_overnight_slot(self):
        """Slot crossing midnight shows both dates."""
        start = timezone.make_aware(datetime(2026, 6, 15, 20, 0))
        end = timezone.make_aware(datetime(2026, 6, 16, 8, 0))

        slots = [{
            'start': start,
            'end': end,
            'duration': calculate_duration(start, end)
        }]

        formatted = format_slots_for_display(slots)

        self.assertEqual(formatted[0]['start_time'], '20:00')
        self.assertEqual(formatted[0]['end_time'], '08:00')
        self.assertEqual(formatted[0]['start_date'], '15 Jun 2026')
        self.assertEqual(formatted[0]['end_date'], '16 Jun 2026')
        self.assertTrue(formatted[0]['crosses_midnight'])