# booking/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
from .models import BookingRequest
from .forms import BookingRequestForm


class BookingRequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Valid booking data
        self.valid_booking_data = {
            'event_title': 'Wedding Reception',
            'event_type': 'private',
            'guest_count': 75,
            'start_datetime': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
            'end_datetime': (timezone.now() + timedelta(days=5, hours=5)).strftime('%Y-%m-%dT%H:%M'),
            'description': '',
            'message': 'Vegetarian options needed',
            'street_address': '123 Main St',
            'postcode': '12345',
            'town_or_city': 'Test City',
            'country': 'US',
        }

    def test_booking_request_get_authenticated(self):
        """Test that authenticated users can access the booking form"""
        self.client.login(username='testuser', password='testpass123')

        # Assuming URL name is 'booking_request' - adjust as needed
        response = self.client.get('/booking/request/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'event_title')
        self.assertIsInstance(response.context['form'], BookingRequestForm)

    def test_booking_request_get_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get('/booking/request/')
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_booking_request_post_valid_data(self):
        """Test successful booking submission with valid data"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post('/booking/request/', self.valid_booking_data)

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Check booking was created
        self.assertEqual(BookingRequest.objects.count(), 1)
        booking = BookingRequest.objects.first()
        self.assertEqual(booking.customer, self.user)
        self.assertEqual(booking.event_title, 'Wedding Reception')
        self.assertEqual(booking.status, 'pending')

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('successfully', str(messages[0]))

    def test_booking_request_post_invalid_data(self):
        """Test booking submission with invalid data"""
        self.client.login(username='testuser', password='testpass123')

        invalid_data = self.valid_booking_data.copy()
        invalid_data['guest_count'] = 50  # Below minimum of 70

        response = self.client.post('/booking/request/', invalid_data)

        # Should return form with errors, not redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'greater than or equal to 70')

        # No booking should be created
        self.assertEqual(BookingRequest.objects.count(), 0)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('correct the errors' in str(msg) for msg in messages))

    def test_booking_request_post_72_hour_validation(self):
        """Test 72-hour advance booking validation in view"""
        self.client.login(username='testuser', password='testpass123')

        invalid_data = self.valid_booking_data.copy()
        # Set start time to only 24 hours in advance
        invalid_data['start_datetime'] = (timezone.now() + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M')
        invalid_data['end_datetime'] = (timezone.now() + timedelta(hours=29)).strftime('%Y-%m-%dT%H:%M')

        response = self.client.post('/booking/request/', invalid_data)

        # Should return form with validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '72 hours')

        # No booking should be created
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_booking_request_post_time_order_validation(self):
        """Test end time after start time validation"""
        self.client.login(username='testuser', password='testpass123')

        invalid_data = self.valid_booking_data.copy()
        start_time = timezone.now() + timedelta(days=5)
        end_time = timezone.now() + timedelta(days=4)  # Before start time

        invalid_data['start_datetime'] = start_time.strftime('%Y-%m-%dT%H:%M')
        invalid_data['end_datetime'] = end_time.strftime('%Y-%m-%dT%H:%M')

        response = self.client.post('/booking/request/', invalid_data)

        # Should return form with validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'End time must be after start time')

        # No booking should be created
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_booking_request_post_open_event_description_required(self):
        """Test that open events require description"""
        self.client.login(username='testuser', password='testpass123')

        invalid_data = self.valid_booking_data.copy()
        invalid_data['event_type'] = 'open'
        invalid_data['description'] = ''  # Empty description

        response = self.client.post('/booking/request/', invalid_data)

        # Should return form with validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Description is required for open events')

        # No booking should be created
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_booking_request_post_unauthenticated(self):
        """Test that unauthenticated users cannot submit bookings"""
        response = self.client.post('/booking/request/', self.valid_booking_data)

        # Should redirect to login, not process the form
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

        # No booking should be created
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_form_initial_state(self):
        """Test that form is properly initialized in GET request"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get('/booking/request/')

        form = response.context['form']
        self.assertIsInstance(form, BookingRequestForm)
        self.assertFalse(form.is_bound)  # Form should not be bound on GET

    def test_file_upload_handling(self):
        """Test that file uploads are handled correctly"""
        self.client.login(username='testuser', password='testpass123')

        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        data_with_file = self.valid_booking_data.copy()
        response = self.client.post('/booking/request/', data_with_file, files={'event_photo': test_image})

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Check booking was created
        self.assertEqual(BookingRequest.objects.count(), 1)
        booking = BookingRequest.objects.first()

        if booking:
            self.assertEqual(booking.event_title, 'Wedding Reception')
        else:
            self.fail("No booking was created")