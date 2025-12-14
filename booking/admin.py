from django import forms
from django.contrib import admin
from django.utils import timezone
from django_summernote.admin import SummernoteModelAdmin
from .models import Booking
from .slots import check_slot_available


class AdminBookingForm(forms.ModelForm):
    """Admin form with booking validation."""

    class Meta:
        model = Booking
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')

        if start and end:
            if end <= start:
                raise forms.ValidationError(
                    'End time must be after start time.')

            error_message = check_slot_available(
                start, end,
                exclude_booking_id=self.instance.pk if self.instance else None
            )
            if error_message:
                raise forms.ValidationError(error_message)

        return cleaned_data


# Register your models here.
@admin.register(Booking)
class BookingAdmin(SummernoteModelAdmin):
    form = AdminBookingForm
    summernote_fields = ('description', 'message')
    list_display = [
        'customer',
        'event_title',
        'start_datetime',
        'status',
        'approved_at']
    list_filter = ['status', 'event_type']
    readonly_fields = ['approved_at', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """
        Auto-set approved_at timestamp when status changes to 'approved'
        Only sets once, never overwrites existing approved_at for
        booking edit validation purposes (if approved_at exist,
        specific booking attributes won't be editable).
        """
        if change:  # when editing an existing booking or booking_request
            booking = Booking.objects.get(pk=obj.pk)
            # set approved_at only if status hasn't been approved yet
            if obj.status == 'approved' and booking.status != 'approved' and booking.approved_at is None:
                obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)