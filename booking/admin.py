from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BookingRequest

# Register your models here.
@admin.register(BookingRequest)
class BookingRequestAdmin(SummernoteModelAdmin):
    summernote_fields = ('description', 'message')
    list_display = ['customer', 'event_title', 'start_datetime', 'status']
    list_filter = ['status', 'event_type']