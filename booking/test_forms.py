# booking/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django import forms
from .forms import BookingRequestForm, check_time_conflicts
from .models import BookingRequest
from events.models import Event


class BookingRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Valid form data for DateTimeInput widgets
        self.valid_data = {
            'event_title': 'Wedding Reception',
            'event_type': 'private',
            'guest_count': 75,  # Above minimum of 70
            'start_datetime': timezone.now() + timedelta(days=20),
            'end_datetime': timezone.now() + timedelta(days=20, hours=5),
            'description': '',  # Optional for private events
            'message': 'Vegetarian options needed',
            'street_address': '123 Main St',
            'postcode': '12345',
            'town_or_city': 'Test City',
            'country': 'US',
        }

    def test_valid_private_event_form(self):
        """Test form is valid for private event without description"""
        form = BookingRequestForm(data=self.valid_data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_valid_open_event_form(self):
        """Test form is valid for open event with description"""
        data = self.valid_data.copy()
        data['event_type'] = 'open'
        data['description'] = 'Community festival celebration'

        form = BookingRequestForm(data=data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_open_event_requires_description(self):
        """Test that open events require a description"""
        data = self.valid_data.copy()
        data['event_type'] = 'open'
        data['description'] = ''  # Empty description

        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Description is required for open events.', form.non_field_errors())

    def test_end_time_after_start_time(self):
        """Test that end time must be after start time"""
        data = self.valid_data.copy()
        data['start_datetime'] = timezone.now() + timedelta(days=20)
        data['end_datetime'] = timezone.now() + timedelta(days=19)  # One day earlier

        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('End time must be after start time.', form.non_field_errors())

    def test_equal_start_end_time_invalid(self):
        """Test that equal start and end times are invalid"""
        data = self.valid_data.copy()
        same_time = timezone.now() + timedelta(days=20)
        data['start_datetime'] = same_time
        data['end_datetime'] = same_time

        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('End time must be after start time.', form.non_field_errors())

    def test_guest_count_minimum_requirement(self):
        """Test minimum guest count validation (must be >= 70)"""
        data = self.valid_data.copy()
        data['guest_count'] = 50  # Below minimum of 70

        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('guest_count', form.errors)
        self.assertIn('Ensure this value is greater than or equal to 70.',
                      str(form.errors['guest_count']))

    def test_guest_count_at_minimum_valid(self):
        """Test that guest count of exactly 70 is valid"""
        data = self.valid_data.copy()
        data['guest_count'] = 70  # Exactly at minimum

        form = BookingRequestForm(data=data)
        self.assertTrue(form.is_valid(), f"Form should be valid with 70 guests. Errors: {form.errors}")

    def test_guest_count_above_minimum_valid(self):
        """Test that guest count above 70 is valid"""
        data = self.valid_data.copy()
        data['guest_count'] = 150  # Well above minimum

        form = BookingRequestForm(data=data)
        self.assertTrue(form.is_valid(), f"Form should be valid with 150 guests. Errors: {form.errors}")

    def test_required_fields(self):
        """Test that required fields are enforced"""
        form = BookingRequestForm(data={})
        self.assertFalse(form.is_valid())

        required_fields = [
            'event_title', 'event_type', 'guest_count',
            'start_datetime', 'end_datetime', 'street_address',
            'postcode'  # Required in your model
        ]

        for field in required_fields:
            self.assertIn(field, form.errors, f"Field {field} should be required")

    def test_optional_fields(self):
        """Test that optional fields work correctly"""
        data = self.valid_data.copy()
        # Remove optional fields
        data['description'] = ''
        data['message'] = ''
        data['country'] = ''

        form = BookingRequestForm(data=data)
        if not form.is_valid():
            print("Optional fields test errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_datetime_input_widget_structure(self):
        """Test that datetime fields use DateTimeInput with datetime-local type"""
        form = BookingRequestForm()
        start_widget = form.fields['start_datetime'].widget
        end_widget = form.fields['end_datetime'].widget
        # Check widget types
        self.assertIsInstance(start_widget, forms.DateTimeInput)
        self.assertIsInstance(end_widget, forms.DateTimeInput)
        # Check HTML5 datetime-local input type
        start_html = start_widget.render('start_datetime', None)
        end_html = end_widget.render('end_datetime', None)
        self.assertIn('type="datetime-local"', start_html)
        self.assertIn('type="datetime-local"', end_html)

    def test_form_save_creates_instance(self):
        """Test form can create a booking instance"""
        form = BookingRequestForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form should be valid. Errors: {form.errors}")

        # Save without committing (customer added in view)
        instance = form.save(commit=False)
        instance.customer = self.user
        instance.save()

        self.assertEqual(instance.event_title, 'Wedding Reception')
        self.assertEqual(instance.customer, self.user)
        self.assertEqual(instance.status, 'pending')  # Default status
        self.assertEqual(instance.guest_count, 75)

    def test_help_text_disclaimer(self):
        """Test that message field has proper disclaimer help text"""
        form = BookingRequestForm()
        message_help_text = form.fields['message'].help_text

        self.assertIn('DISCLAIMER', message_help_text)
        self.assertIn('no dietary considerations will be taken', message_help_text)

    def test_placeholder_text(self):
        """Test that textarea fields have proper placeholder text"""
        form = BookingRequestForm()

        description_placeholder = form.fields['description'].widget.attrs.get('placeholder')
        message_placeholder = form.fields['message'].widget.attrs.get('placeholder')

        self.assertIn('Event details', description_placeholder)
        self.assertIn('Special requests', message_placeholder)

    def test_15_days_advance_booking_requirement(self):
        """Test that events must be booked at least 15 days in advance"""
        data = self.valid_data.copy()

        # Use a fixed point in time to avoid race conditions
        now = timezone.now()
        data['start_datetime'] = now + timedelta(days=10)  # Only 10 days (< 15)
        data['end_datetime'] = now + timedelta(days=10, hours=5)    # 5 hours after start

        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('15 days', str(form.non_field_errors()))


class CheckTimeConflictsTest(TestCase):
    """Test the check_time_conflicts function."""

    def setUp(self):
        """Create test user and base datetime."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        # Base date: 20 days from now (passes 15-day rule)
        self.base_date = timezone.now() + timedelta(days=20)

    def create_booking(self, start_hour, end_hour, days_offset=0, status='approved'):
        """Helper to create bookings at specific hours."""
        start = self.base_date.replace(
            hour=start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)
        end = self.base_date.replace(
            hour=end_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)

        # Handle overnight events
        if end_hour < start_hour:
            end += timedelta(days=1)

        return BookingRequest.objects.create(
            customer=self.user,
            event_title='Test Booking',
            event_type='private',
            guest_count=70,
            start_datetime=start,
            end_datetime=end,
            status=status,
            street_address='123 Test St',
            postcode='12345'
        )

    def create_event(self, start_hour, end_hour, days_offset=0, status='active'):
        """Helper to create events at specific hours."""
        start = self.base_date.replace(
            hour=start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)
        end = self.base_date.replace(
            hour=end_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)

        if end_hour < start_hour:
            end += timedelta(days=1)

        return Event.objects.create(
            admin=self.admin,
            event_title='Test Event',
            event_type='open',
            start_datetime=start,
            end_datetime=end,
            status=status,
            description='Test event description'
        )

    def get_test_times(self, start_hour, end_hour, days_offset=0):
        """Helper to get start/end datetimes for testing."""
        start = self.base_date.replace(
            hour=start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)
        end = self.base_date.replace(
            hour=end_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)

        if end_hour < start_hour:
            end += timedelta(days=1)

        return start, end

    # ========== NO CONFLICT TESTS ==========

    def test_no_conflicts_empty_database(self):
        """No conflicts when no bookings or events exist."""
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    def test_no_conflict_10_hour_gap_after(self):
        """No conflict when new booking starts 10+ hours after existing ends."""
        # Existing: 08:00-12:00
        self.create_booking(8, 12)
        # New: 22:00-23:00 (10 hour gap)
        start, end = self.get_test_times(22, 23)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    def test_no_conflict_10_hour_gap_before(self):
        """No conflict when new booking ends 10+ hours before existing starts."""
        # Existing: 20:00-23:00
        self.create_booking(20, 23)
        # New: 06:00-10:00 (10 hour gap)
        start, end = self.get_test_times(6, 10)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    def test_no_conflict_cancelled_booking(self):
        """Cancelled bookings should not cause conflicts."""
        self.create_booking(10, 14, status='cancelled')
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    def test_no_conflict_rejected_booking(self):
        """Rejected bookings should not cause conflicts."""
        self.create_booking(10, 14, status='rejected')
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    def test_no_conflict_inactive_event(self):
        """Inactive events should not cause conflicts."""
        self.create_event(10, 14, status='cancelled')
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)

    # ========== BEFORE CONFLICT TESTS ==========

    def test_conflict_before_insufficient_gap(self):
        """Conflict when starting too soon after existing event."""
        # Existing: 08:00-12:00
        self.create_booking(8, 12)
        # New: 20:00-22:00 (only 8 hour gap)
        start, end = self.get_test_times(20, 22)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        self.assertIn('conflicts', result)
        self.assertIn('later', result)

    def test_conflict_before_suggests_correct_time(self):
        """Should suggest starting 10 hours after existing ends."""
        # Existing: 08:00-12:00
        self.create_booking(8, 12)
        # New: 18:00-20:00 (only 6 hour gap)
        start, end = self.get_test_times(18, 20)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        # Should suggest 22:00 (12:00 + 10 hours)
        self.assertIn('22:00', result)

    # ========== AFTER CONFLICT TESTS ==========

    def test_conflict_after_insufficient_gap(self):
        """Conflict when ending too close to upcoming event."""
        # Existing: 20:00-23:00
        self.create_booking(20, 23)
        # New: 08:00-12:00 (only 8 hour gap)
        start, end = self.get_test_times(8, 12)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        self.assertIn('conflicts', result)
        self.assertIn('earlier', result)

    def test_conflict_after_suggests_correct_time(self):
        """Should suggest ending 10 hours before existing starts."""
        # Existing: 20:00-23:00
        self.create_booking(20, 23)
        # New: 08:00-14:00 (only 6 hour gap)
        start, end = self.get_test_times(8, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        # Should suggest ending by 10:00 (20:00 - 10 hours)
        self.assertIn('10:00', result)

    # ========== BOTH END CONFLICT TESTS ==========

    def test_sandwich_conflict_with_available_window(self):
        """Sandwich conflict shows available window when space exists."""
        # Before: 02:00-04:00 (day 0)
        self.create_booking(2, 4)
        # After: 04:00-06:00 (day 1) - next day, creates sandwich
        self.create_booking(4, 6, days_offset=1)
        # New: 08:00-20:00 (day 0) - triggers sandwich
        # Window should be: 14:00 (04:00+10) to 18:00 (04:00-10) = 4 hours
        start, end = self.get_test_times(8, 20)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        self.assertIn('window', result)

    def test_sandwich_conflict_no_available_window(self):
        """Sandwich conflict with no space suggests different date."""
        # Before: 06:00-10:00
        self.create_booking(6, 10)
        # After: 20:00-23:00 (only 10 hours between, no room for event + gaps)
        self.create_booking(20, 23)
        # New: 12:00-18:00 (no valid window)
        start, end = self.get_test_times(12, 18)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)
        self.assertIn('different date', result.lower())

    # ========== OVERLAP TESTS ==========

    def test_conflict_direct_overlap(self):
        """Direct time overlap causes conflict."""
        # Existing: 10:00-14:00
        self.create_booking(10, 14)
        # New: 12:00-16:00 (overlaps)
        start, end = self.get_test_times(12, 16)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)

    def test_conflict_contained_within(self):
        """New booking fully within existing causes conflict."""
        # Existing: 08:00-18:00
        self.create_booking(8, 18)
        # New: 10:00-14:00 (inside existing)
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)

    # ========== EXCLUDE BOOKING ID TESTS ==========

    def test_exclude_booking_id_no_self_conflict(self):
        """Booking should not conflict with itself when editing."""
        booking = self.create_booking(10, 14)
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end, exclude_booking_id=booking.pk)
        self.assertIsNone(result)

    def test_exclude_booking_id_still_checks_others(self):
        """Excluding one booking should still check others."""
        booking1 = self.create_booking(10, 14)
        self.create_booking(10, 14, days_offset=1)
        # Check same time as second, excluding booking1
        start, end = self.get_test_times(10, 14, days_offset=1)
        result = check_time_conflicts(start, end, exclude_booking_id=booking1.pk)
        self.assertIsNotNone(result)

    # ========== EVENT CONFLICT TESTS ==========

    def test_conflict_with_active_event(self):
        """Active events should cause conflicts."""
        self.create_event(10, 14)
        start, end = self.get_test_times(10, 14)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)

    def test_conflict_event_and_booking_combined(self):
        """Should check both events and bookings for conflicts."""
        # Booking before
        self.create_booking(6, 8)
        # Event after
        self.create_event(22, 23)
        # New in middle with insufficient gaps
        start, end = self.get_test_times(10, 20)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)

    # ========== OVERNIGHT EVENT TESTS ==========

    def test_overnight_event_conflict(self):
        """Overnight events (ending next day) should be handled."""
        # Existing: 20:00-02:00 (next day)
        self.create_booking(20, 2)
        # New: 08:00-10:00 on NEXT DAY (only 6 hours after overnight ends at 02:00)
        start, end = self.get_test_times(8, 10, days_offset=1)
        result = check_time_conflicts(start, end)
        self.assertIsNotNone(result)

    def test_overnight_event_no_conflict_with_gap(self):
        """Overnight event with sufficient gap should not conflict."""
        # Existing: 20:00-02:00 (next day)
        self.create_booking(20, 2)
        # New: 12:00-14:00 on NEXT DAY (10 hours after 02:00)
        start, end = self.get_test_times(12, 14, days_offset=1)
        result = check_time_conflicts(start, end)
        self.assertIsNone(result)