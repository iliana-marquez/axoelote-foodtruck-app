from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BookingRequestForm
from .rules import MINIMUM_ADVANCE_DAYS, MINIMUM_GUESTS


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