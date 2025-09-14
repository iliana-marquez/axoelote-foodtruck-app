from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from booking.models import BookingRequest


class BookingRequestModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='Password123!')

    def test_create_booking_request(self):
        # Create a BookingRequest
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=3)

        booking = BookingRequest.objects.create(
            customer=self.user,
            event_title="Test Event",
            event_type="open",
            guest_count=50,
            start_datetime=start_time,
            end_datetime=end_time,
            description="Test description",
            message="Test message",
            status="pending",
            street_address="123 Test Street",
            postcode="1010",
            town_or_city="Vienna",
            country="AT",
        )

        # Fetch from DB
        saved_booking = BookingRequest.objects.get(id=booking.id)

        # Assertions
        self.assertEqual(saved_booking.customer.username, 'testuser')
        self.assertEqual(saved_booking.event_title, "Test Event")
        self.assertEqual(saved_booking.guest_count, 50)
        self.assertEqual(saved_booking.status, "pending")
        self.assertEqual(saved_booking.street_address, "123 Test Street")
        self.assertEqual(saved_booking.town_or_city, "Vienna")
        self.assertEqual(saved_booking.country.code, "AT")