from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import BookingRequestForm
from .slots import get_available_slots, format_slots_for_display
from .rules import MINIMUM_ADVANCE_DAYS, MINIMUM_GUESTS
from .models import Booking
from .utils import get_edit_permissions


@login_required(login_url='account_login')
def booking_request(request):
    """
    renders the booking request form and handles form submission
    """

    if request.method == 'POST':
        form = BookingRequestForm(request.POST, request.FILES)
        if form.is_valid():
            # Save booking but don't commit yet
            booking = form.save(commit=False)
            # Add the current user as the customer
            booking.customer = request.user
            booking.save()
            # Build in messages
            messages.success(request, 'Booking request submitted successfully! We will respond within 48 hours.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = BookingRequestForm()

    return render(
        request, 'booking/booking_request.html',
        {
            'form': form,
            'min_advance_days': MINIMUM_ADVANCE_DAYS,
            'min_guests': MINIMUM_GUESTS,
        }
    )


@login_required(login_url='account_login')
def get_slots_for_date(request, date_str):
    """
    API endpoint to get available slots for a specific date.
    Returns JSON with available time slots.
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }, status=400)

    # check if date is far enough in advance
    min_date = (timezone.now() + timedelta(days=MINIMUM_ADVANCE_DAYS)).date()
    if target_date < min_date:
        return JsonResponse({
            'success': False,
            'error': f"Date must be at least {
                MINIMUM_ADVANCE_DAYS} days in advance."
        }, status=400)

    slots = get_available_slots(target_date)
    formatted_slots = format_slots_for_display(slots)

    return JsonResponse({
        'success': True,
        'date': date_str,
        'slots': formatted_slots,
        'has_availability': len(formatted_slots) > 0
    })


class BookingList(LoginRequiredMixin, generic.ListView):
    """
    Display list of user's bookings.
    Filtered by current user with status counts for tabs.
    """
    model = Booking
    template_name = 'booking/bookings.html'
    context_object_name = 'bookings'
    login_url = 'account_login'

    def get_queryset(self):
        """Return only bookings for current user."""
        return Booking.objects.filter(
            customer=self.request.user
        ).order_by('-start_datetime')

    def get_context_data(self, **kwargs):
        """Add status counts for tabs."""
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        bookings = self.get_queryset()

        context['pending_count'] = bookings.filter(status='pending').count()
        context['approved_count'] = bookings.filter(status='approved').count()
        context['active_count'] = bookings.filter(
            status='approved', start_datetime__gte=today
        ).count()
        context['past_count'] = bookings.filter(
            start_datetime__lt=today).count()

        return context


@login_required(login_url='account_login')
def booking_detail(request, pk):
    """
    Booking details page (read-only).
    Shows full booking info.
    """
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)

    return render(request, 'booking/booking_detail.html', {
        'booking': booking,
    })


@login_required(login_url='account_login')
def booking_edit(request, pk):
    """
    Edit a booking based on tiered permissions.

    - 15+ days: Full edit
    - 3-14 days: Cosmetic only (title, description, photo)
    - 0-2 days: No edit, contact admin
    """
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    permissions = get_edit_permissions(booking)

    # Check if editing is allowed
    if not permissions['can_edit']:
        messages.error(request, permissions['message'])
        return redirect('booking_detail', pk=pk)

    if request.method == 'POST':
        if permissions['edit_level'] == 'full':
            # Full edit - all fields
            form = BookingRequestForm(
                request.POST,
                request.FILES,
                instance=booking
                )
        else:
            # Cosmetic edit - only allowed fields
            form = BookingRequestForm(
                request.POST,
                request.FILES,
                instance=booking
                )
            # Restore locked fields from original booking
            for field in permissions['locked_fields']:
                if field in form.fields:
                    form.instance.__dict__[field] = getattr(booking, field)

        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('booking_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingRequestForm(instance=booking)

    return render(request, 'booking/booking_edit.html', {
        'form': form,
        'booking': booking,
        'permissions': permissions,
        'min_advance_days': MINIMUM_ADVANCE_DAYS,
        'min_guests': MINIMUM_GUESTS,
    })