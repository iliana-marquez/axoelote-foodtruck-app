from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
from events.models import Event
from .models import RegularSchedule


def get_schedule_for_date(target_date):
    """Get schedule item for a specific date with priority logic"""
    # Priority 1: Active events
    events = Event.objects.filter(
        start_datetime__date__lte=target_date,  # Event starts on or before target date
        end_datetime__date__gte=target_date,    # Event ends on or after target date
        status='active'
    )
    if events.exists():
        return events.first(), 'event'

    # Priority 2: Approved bookings
    approved_bookings = Booking.objects.filter(
        start_datetime__date__lte=target_date,
        end_datetime__date__gte=target_date,
        status='approved'
    )
    if approved_bookings.exists():
        return approved_bookings.first(), 'booking'

    # Priority 3: Regular schedule
    regular = RegularSchedule.objects.filter(is_active=True).first()
    if regular:
        day_name = target_date.strftime('%A')
        if regular.is_open_on_day(day_name):
            return regular, 'regular'

    return None, 'closed'


def index(request):
    today = timezone.now().date()
    schedule_data = []

    for i in range(9):  # Today + next days
        date = today + timedelta(days=i)
        schedule_item, schedule_type = get_schedule_for_date(date)
        schedule_data.append({
            'date': date,
            'item': schedule_item,
            'type': schedule_type,
            'is_today': i == 0
        })

    return render(request, "home/index.html", {
        'schedule_data': schedule_data
    })