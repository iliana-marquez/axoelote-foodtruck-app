from django.contrib import admin
from .models import RegularSchedule

@admin.register(RegularSchedule)
class RegularScheduleAdmin(admin.ModelAdmin):
    list_display = ['venue_name', 'get_operating_days', 'opening_time', 'closing_time', 'is_active']
    
    def get_operating_days(self, obj):
        """Custom method for cleaner admin display"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_abbrevs = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        active_days = [day_abbrevs[i] for i, day in enumerate(days) if getattr(obj, day)]
        
        if not active_days:
            return "Closed"
        elif len(active_days) == 1:
            return active_days[0]
        else:
            # Check if consecutive
            day_indices = [i for i, day in enumerate(days) if getattr(obj, day)]
            consecutive = all(day_indices[i] + 1 == day_indices[i + 1] for i in range(len(day_indices) - 1))
            
            return f"{active_days[0]} - {active_days[-1]}" if consecutive else ", ".join(active_days)
    
    get_operating_days.short_description = 'Operating Days'