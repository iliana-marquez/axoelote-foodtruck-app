from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django_summernote.admin import SummernoteModelAdmin
from .models import Event


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter admin field to only show staff users
        self.fields['admin'].queryset = User.objects.filter(is_staff=True)


@admin.register(Event)
class EventAdmin(SummernoteModelAdmin):
    form = EventAdminForm
    summernote_fields = ('description', 'message')
    list_display = ['admin', 'event_title', 'start_datetime', 'event_type', 'status']
    list_filter = ['status', 'event_type', 'created_at']
    search_fields = ['event_title', 'description']