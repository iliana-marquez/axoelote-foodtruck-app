"""
Tests for slot availability calculation.
Covers engagements fetching, slot calculation, and exclude logic.

Updated for USE_TZ=False (naive datetimes)
"""

from datetime import date, time, datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from booking.models import Booking
from booking.slots import (
    get_engagements_for_date_range,
    get_available_slots,
    check_slot_available,
    format_slots_for_display
)
from booking.rules import MINIMUM_GAP_HOURS, MINIMUM_ADVANCE_DAYS
from events.models import Event


class EngagementsTestCase(TestCase):
    """Test get_engagements_for_date_range function."""
    
    def setUp(self):
        """Create test user and sample data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            is_staff=True
        )
        
        # Target date for testing (far enough in future)
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
    def test_fetches_pending_bookings(self):
        """Pending bookings should be included in engagements."""
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Pending Booking',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='pending'
        )
        
        engagements = get_engagements_for_date_range(
            self.target_date - timedelta(days=1),
            self.target_date + timedelta(days=1)
        )
        
        self.assertEqual(len(engagements), 1)
        self.assertEqual(engagements[0]['start'], booking.start_datetime)
        self.assertEqual(engagements[0]['end'], booking.end_datetime)
        
    def test_fetches_approved_bookings(self):
        """Approved bookings should be included in engagements."""
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Approved Booking',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        engagements = get_engagements_for_date_range(
            self.target_date - timedelta(days=1),
            self.target_date + timedelta(days=1)
        )
        
        self.assertEqual(len(engagements), 1)
        
    def test_excludes_cancelled_bookings(self):
        """Cancelled bookings should NOT be included."""
        Booking.objects.create(
            customer=self.user,
            event_title='Cancelled Booking',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='cancelled'
        )
        
        engagements = get_engagements_for_date_range(
            self.target_date - timedelta(days=1),
            self.target_date + timedelta(days=1)
        )
        
        self.assertEqual(len(engagements), 0)
        
    def test_fetches_active_events(self):
        """Active events should be included in engagements."""
        event = Event.objects.create(
            admin=self.admin_user,
            event_title='Test Event',
            event_type='private',
            start_datetime=datetime.combine(self.target_date, time(18, 0)),
            end_datetime=datetime.combine(self.target_date, time(22, 0)),
            status='active'
        )
        
        engagements = get_engagements_for_date_range(
            self.target_date - timedelta(days=1),
            self.target_date + timedelta(days=1)
        )
        
        self.assertEqual(len(engagements), 1)
        self.assertEqual(engagements[0]['start'], event.start_datetime)
        
    def test_fetches_multiple_engagements(self):
        """Should fetch both bookings and events."""
        # Create booking
        Booking.objects.create(
            customer=self.user,
            event_title='Test Booking',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        # Create event
        Event.objects.create(
            admin=self.admin_user,
            event_title='Test Event',
            event_type='private',
            start_datetime=datetime.combine(self.target_date, time(18, 0)),
            end_datetime=datetime.combine(self.target_date, time(22, 0)),
            status='active'
        )
        
        engagements = get_engagements_for_date_range(
            self.target_date - timedelta(days=1),
            self.target_date + timedelta(days=1)
        )
        
        self.assertEqual(len(engagements), 2)


class AvailableSlotsTestCase(TestCase):
    """Test get_available_slots function."""
    
    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            is_staff=True
        )
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
    def test_fully_available_when_no_engagements(self):
        """Empty day should return full availability."""
        slots = get_available_slots(self.target_date)
        
        self.assertGreater(len(slots), 0)
        
    def test_no_availability_when_fully_booked(self):
        """Day with all-day event should return no slots."""
        # Create event covering entire day plus gap requirements
        Event.objects.create(
            admin=self.admin_user,
            event_title='All Day Event',
            event_type='private',
            start_datetime=datetime.combine(
                self.target_date - timedelta(days=1), time(12, 0)
            ),
            end_datetime=datetime.combine(
                self.target_date + timedelta(days=1), time(12, 0)
            ),
            status='active'
        )
        
        slots = get_available_slots(self.target_date)
        
        self.assertEqual(len(slots), 0)
        
    def test_partial_availability_with_booking(self):
        """Day with partial booking should return available windows."""
        # Create booking in middle of day
        Booking.objects.create(
            customer=self.user,
            event_title='Midday Booking',
            start_datetime=datetime.combine(self.target_date, time(12, 0)),
            end_datetime=datetime.combine(self.target_date, time(16, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        slots = get_available_slots(self.target_date)
        
        print(f"\nPartial availability test:")
        print(f"Target date: {self.target_date}")
        print(f"Slots returned: {slots}")
        for slot in slots:
            print(f"  Slot: {slot['start']} - {slot['end']}")


class ExcludeBookingTestCase(TestCase):
    """Test exclude_booking_id parameter for editing."""
    
    def setUp(self):
        """Create test user and booking."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
        # Create a booking that we'll try to edit
        self.booking = Booking.objects.create(
            customer=self.user,
            event_title='Booking To Edit',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='pending'
        )
        
    def test_own_booking_blocks_without_exclude(self):
        """Without exclude, own booking should block the slot."""
        slots = get_available_slots(self.target_date)
        
        print(f"\nWithout exclude:")
        print(f"Booking: {self.booking.start_datetime} - {self.booking.end_datetime}")
        print(f"Slots: {slots}")
        
    def test_own_booking_available_with_exclude(self):
        """With exclude, own booking's slot should be available."""
        slots = get_available_slots(
            self.target_date,
            exclude_booking_id=self.booking.pk
        )
        
        print(f"\nWith exclude (ID={self.booking.pk}):")
        print(f"Booking: {self.booking.start_datetime} - {self.booking.end_datetime}")
        print(f"Slots: {slots}")
        
        # Should have availability now
        self.assertGreater(len(slots), 0)
        
    def test_own_booking_available_with_exclude_as_string(self):
        """With exclude as string (from URL), own booking's slot should be available."""
        slots = get_available_slots(
            self.target_date,
            exclude_booking_id=str(self.booking.pk)  # String like from URL param
        )
        
        print(f"\nWith exclude as string (ID='{self.booking.pk}'):")
        print(f"Slots: {slots}")
        
        # Should have availability now
        self.assertGreater(len(slots), 0)
        
    def test_exclude_only_affects_own_booking(self):
        """Exclude should not affect other bookings."""
        # Create another booking on same day
        other_booking = Booking.objects.create(
            customer=self.user,
            event_title='Other Booking',
            start_datetime=datetime.combine(self.target_date, time(18, 0)),
            end_datetime=datetime.combine(self.target_date, time(22, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        slots = get_available_slots(
            self.target_date,
            exclude_booking_id=self.booking.pk
        )
        
        print(f"\nExclude with other booking:")
        print(f"Own booking: {self.booking.start_datetime} - {self.booking.end_datetime}")
        print(f"Other booking: {other_booking.start_datetime} - {other_booking.end_datetime}")
        print(f"Slots: {slots}")


class SlotsAPITestCase(TestCase):
    """Test get_slots_for_date API endpoint."""
    
    def setUp(self):
        """Create test user and client."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
    def test_api_returns_json(self):
        """API should return JSON response."""
        url = f"/booking/slots/{self.target_date.strftime('%Y-%m-%d')}/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
    def test_api_returns_success_structure(self):
        """API should return expected structure."""
        url = f"/booking/slots/{self.target_date.strftime('%Y-%m-%d')}/"
        response = self.client.get(url)
        
        data = response.json()
        
        self.assertIn('success', data)
        self.assertIn('date', data)
        self.assertIn('slots', data)
        self.assertIn('has_availability', data)
        
    def test_api_exclude_parameter(self):
        """API should accept and use exclude parameter."""
        # Create booking
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Test Booking',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='pending'
        )
        
        # Without exclude
        url_without = f"/booking/slots/{self.target_date.strftime('%Y-%m-%d')}/"
        response_without = self.client.get(url_without)
        data_without = response_without.json()
        
        # With exclude
        url_with = f"/booking/slots/{self.target_date.strftime('%Y-%m-%d')}/?exclude={booking.pk}"
        response_with = self.client.get(url_with)
        data_with = response_with.json()
        
        print(f"\nAPI exclude test:")
        print(f"Without exclude: has_availability={data_without['has_availability']}, slots={len(data_without['slots'])}")
        print(f"With exclude: has_availability={data_with['has_availability']}, slots={len(data_with['slots'])}")
        
        # With exclude should have availability
        self.assertTrue(data_with['has_availability'])
        
    def test_api_rejects_past_dates(self):
        """API should reject dates too soon."""
        past_date = date.today() + timedelta(days=1)  # Too soon
        url = f"/booking/slots/{past_date.strftime('%Y-%m-%d')}/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])


class CheckSlotAvailableTestCase(TestCase):
    """Test check_slot_available validation function."""
    
    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            is_staff=True
        )
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
    def test_returns_none_when_available(self):
        """Should return None when slot is available."""
        start = datetime.combine(self.target_date, time(10, 0))
        end = datetime.combine(self.target_date, time(14, 0))
        
        result = check_slot_available(start, end)
        
        self.assertIsNone(result)
        
    def test_returns_error_when_conflict(self):
        """Should return error message when slot conflicts."""
        # Create existing booking
        Booking.objects.create(
            customer=self.user,
            event_title='Existing Booking',
            start_datetime=datetime.combine(self.target_date, time(12, 0)),
            end_datetime=datetime.combine(self.target_date, time(16, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        # Try to book overlapping slot
        start = datetime.combine(self.target_date, time(14, 0))
        end = datetime.combine(self.target_date, time(18, 0))
        
        result = check_slot_available(start, end)
        
        self.assertIsNotNone(result)
        self.assertIn('Conflicts', result)
        
    def test_respects_minimum_gap(self):
        """Should enforce minimum gap between bookings."""
        # Create existing booking
        Booking.objects.create(
            customer=self.user,
            event_title='Existing Booking',
            start_datetime=datetime.combine(self.target_date, time(12, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        # Try to book right after (within gap period)
        start = datetime.combine(self.target_date, time(15, 0))  # Only 1 hour gap
        end = datetime.combine(self.target_date, time(18, 0))
        
        result = check_slot_available(start, end)
        
        self.assertIsNotNone(result)
        self.assertIn(str(MINIMUM_GAP_HOURS), result)
        
    def test_exclude_own_booking(self):
        """Should exclude own booking when editing."""
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Booking To Edit',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='pending'
        )
        
        # Same slot should be available when excluding own booking
        start = datetime.combine(self.target_date, time(10, 0))
        end = datetime.combine(self.target_date, time(14, 0))
        
        result = check_slot_available(start, end, exclude_booking_id=booking.pk)
        
        self.assertIsNone(result)
        
    def test_exclude_as_string(self):
        """Should handle exclude_booking_id as string."""
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Booking To Edit',
            start_datetime=datetime.combine(self.target_date, time(10, 0)),
            end_datetime=datetime.combine(self.target_date, time(14, 0)),
            guest_count=100,
            status='pending'
        )
        
        start = datetime.combine(self.target_date, time(10, 0))
        end = datetime.combine(self.target_date, time(14, 0))
        
        # Pass as string (like from URL param)
        result = check_slot_available(start, end, exclude_booking_id=str(booking.pk))
        
        self.assertIsNone(result)
        
    def test_conflicts_with_events(self):
        """Should detect conflicts with events."""
        Event.objects.create(
            admin=self.admin_user,
            event_title='Existing Event',
            event_type='private',
            start_datetime=datetime.combine(self.target_date, time(18, 0)),
            end_datetime=datetime.combine(self.target_date, time(22, 0)),
            status='active'
        )
        
        # Try to book overlapping with event
        start = datetime.combine(self.target_date, time(16, 0))
        end = datetime.combine(self.target_date, time(20, 0))
        
        result = check_slot_available(start, end)
        
        self.assertIsNotNone(result)
        self.assertIn('Conflicts', result)


class NaiveDatetimeTestCase(TestCase):
    """Test that naive datetimes work correctly with USE_TZ=False."""
    
    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.target_date = date.today() + timedelta(days=MINIMUM_ADVANCE_DAYS + 10)
        
    def test_booking_stores_naive_datetime(self):
        """Bookings should store naive datetimes."""
        start = datetime.combine(self.target_date, time(10, 0))
        end = datetime.combine(self.target_date, time(14, 0))
        
        booking = Booking.objects.create(
            customer=self.user,
            event_title='Naive TZ Test',
            start_datetime=start,
            end_datetime=end,
            guest_count=100,
            status='pending'
        )
        
        # Reload from DB
        booking.refresh_from_db()
        
        print(f"\nNaive datetime test:")
        print(f"Input start: {start}")
        print(f"Stored start: {booking.start_datetime}")
        print(f"Times match: {booking.start_datetime.replace(tzinfo=None) == start or booking.start_datetime == start}")
        
        # Times should match (no UTC conversion)
        self.assertEqual(booking.start_datetime.hour, 10)
        self.assertEqual(booking.end_datetime.hour, 14)
        
    def test_slot_times_match_booking_times(self):
        """Slot window should correctly reflect booking times."""
        Booking.objects.create(
            customer=self.user,
            event_title='Slot Time Test',
            start_datetime=datetime.combine(self.target_date, time(12, 0)),
            end_datetime=datetime.combine(self.target_date, time(16, 0)),
            guest_count=100,
            status='approved',
            approved_at=datetime.now()
        )
        
        slots = get_available_slots(self.target_date)
        formatted = format_slots_for_display(slots)
        
        print(f"\nSlot time match test:")
        print(f"Booking: 12:00 - 16:00")
        print(f"Formatted slots:")
        for slot in formatted:
            print(f"  {slot['start_time']} - {slot['end_time']}")