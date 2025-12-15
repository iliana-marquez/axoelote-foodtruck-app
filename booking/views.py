from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import BookingRequestForm
from .slots import get_available_slots, format_slots_for_display
from .models import Booking
from .utils import get_edit_permissions, get_status_timestamp
from .rules import (
    MINIMUM_ADVANCE_DAYS,
    MINIMUM_GUESTS,
    CONTACT_EMAIL,
    CONTACT_PHONE
    )


# =========================================
# CLASS-BASED VIEWS
# =========================================


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

        bookings_with_permissions = []
        for booking in bookings:
            booking.permissions = get_edit_permissions(booking)
            bookings_with_permissions.append(booking)

        context['bookings'] = bookings_with_permissions
        context['pending_count'] = bookings.filter(status='pending').count()
        context['approved_count'] = bookings.filter(status='approved').count()
        context['active_count'] = bookings.filter(
            status='approved', start_datetime__gte=today
        ).count()
        context['past_count'] = bookings.filter(
            start_datetime__lt=today).count()

        return context


class BookingDetailView(LoginRequiredMixin, View):
    """
    Booking detail with inline editing.
    GET: Display booking with edit sections
    POST: Save changes
    """
    login_url = 'account_login'

    def get_booking(self, pk):
        """
        get Booking owned by current user
        """
        return get_object_or_404(
            Booking, pk=pk, customer=self.request.user
        )

    def get(self, request, pk):
        """
        Display bookings details with inline edit forms
        """
        booking = self.get_booking(pk)
        permissions = get_edit_permissions(booking)
        form = BookingRequestForm(instance=booking)
        status_info = get_status_timestamp(booking)

        return render(
            request,
            'booking/booking_detail.html',
            {
                'booking': booking,
                'form': form,
                'permissions': permissions,
                'status_info': status_info,
                'min_advance_days': MINIMUM_ADVANCE_DAYS,
                'min_guests': MINIMUM_GUESTS,
                'contact_email': CONTACT_EMAIL,
                'contact_phone': CONTACT_PHONE,
            }
        )

    def post(self, request, pk):
        """
        Handle inline edit submission.
        """
        booking = self.get_booking(pk)
        permissions = get_edit_permissions(booking)
        status_info = get_status_timestamp(booking)

        # Check if editing is allowed
        if not permissions['can_edit']:
            messages.error(request, permissions['message'])
            return redirect('booking_detail', pk=pk)

        # Handle delete
        if request.POST.get('action') == 'cancel':
            event_title = booking.event_title
            booking.delete()
            messages.success(request, f'"{event_title}" has been deleted.')
            return redirect('bookings')

        form = BookingRequestForm(
            request.POST,
            request.FILES,
            instance=booking
            )

        if form.is_valid():
            # Restore locked fields for cosmetic edit
            if permissions['edit_level'] == 'cosmetic':
                for field in permissions['locked_fields']:
                    if hasattr(booking, field):
                        setattr(form.instance, field, getattr(booking, field))

            form.save()
            messages.success(request, "Booking updated successfully")
            return redirect('booking_detail', pk=pk)

        # Invalid form: re-render with errors
        messages.error(request, 'Please correct the errors below.')
        return render(
            request,
            'booking/booking_detail.html',
            {
                'booking': booking,
                'form': form,
                'permissions': permissions,
                'status_info': status_info,
                'min_advance_days': MINIMUM_ADVANCE_DAYS,
                'min_guests': MINIMUM_GUESTS,
                'contact_email': CONTACT_EMAIL,
                'contact_phone': CONTACT_PHONE,
            }
        )

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

    Query params:
        exclude: Booking ID to exclude from conflict chek for editing
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

    # get exclude ID for edit mode
    exclude_id = request.GET.get('exclude')

    slots = get_available_slots(target_date, exclude_booking_id=exclude_id)
    formatted_slots = format_slots_for_display(slots)

    return JsonResponse({
        'success': True,
        'date': date_str,
        'slots': formatted_slots,
        'has_availability': len(formatted_slots) > 0
    })