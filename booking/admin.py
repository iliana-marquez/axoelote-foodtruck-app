from django.contrib import admin
from django.utils import timezone
from django_summernote.admin import SummernoteModelAdmin
from .models import BookingRequest


# Register your models here.
@admin.register(BookingRequest)
class BookingRequestAdmin(SummernoteModelAdmin):
    summernote_fields = ('description', 'message')
    list_display = ['customer', 'event_title', 'start_datetime', 'status', 'approved_at']
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
            booking = BookingRequest.objects.get(pk=obj.pk)
            # set approved_at only if status hasn't been approved yet
            if obj.status == 'approved' and booking.status != 'approved' and booking.approved_at is None:
                obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)