# booking/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django import forms
from .forms import BookingRequestForm


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
            'start_datetime': timezone.now() + timedelta(days=5),
            'end_datetime': timezone.now() + timedelta(days=5, hours=5),
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
        data['start_datetime'] = timezone.now() + timedelta(days=5)
        data['end_datetime'] = timezone.now() + timedelta(days=4)  # One day earlier
        
        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('End time must be after start time.', form.non_field_errors())

    def test_equal_start_end_time_invalid(self):
        """Test that equal start and end times are invalid"""
        data = self.valid_data.copy()
        same_time = timezone.now() + timedelta(days=5)
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

    def test_72_hours_advance_booking_requirement(self):
        """Test that events must be booked at least 72 hours in advance"""
        data = self.valid_data.copy()
        
        # Use a fixed point in time to avoid race conditions
        now = timezone.now()
        data['start_datetime'] = now + timedelta(hours=48)  # Only 48 hours (< 72)
        data['end_datetime'] = now + timedelta(hours=53)    # 5 hours after start
        
        form = BookingRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Events must be booked at least 72 hours (3 days) in advance.', 
                      form.non_field_errors())