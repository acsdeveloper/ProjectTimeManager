# from django.contrib import admin
# from .models import Project, ProjectTimer

# class ProjectAdmin(admin.ModelAdmin):
#     list_display = (
#         'user', 'title', 'submitted_at', 'hours_assigned', 'display_tracked_time','is_submitted'
#     )

#     def display_tracked_time(self, obj):
#         if obj.tracked_time:
#             total_seconds = int(obj.tracked_time.total_seconds())
#             hours = total_seconds // 3600
#             minutes = (total_seconds % 3600) // 60
#             return f"{hours}h {minutes}m"
#         return "0h 0m"

#     display_tracked_time.short_description = 'Hours Worked'

# admin.site.register(Project, ProjectAdmin)


from django.contrib import admin
from .models import Project, ProjectTimer

class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'title',
        'submitted_at',
        'hours_assigned',
        'display_tracked_time',
        'display_time_difference',
        'is_submitted'
    )

    def display_tracked_time(self, obj):
        if obj.tracked_time:
            total_seconds = int(obj.tracked_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    display_tracked_time.short_description = 'Hours Worked'

    def display_time_difference(self, obj):
        if obj.tracked_time and obj.hours_assigned:
            assigned_hours = float(obj.hours_assigned)
            tracked_hours = obj.tracked_time.total_seconds() / 3600
            diff = round(tracked_hours - assigned_hours, 2)
            if diff > 0:
                return f"{diff}h (Over)"
            elif diff < 0:
                return f"{diff}h (Remaining)"
            else:
                return "On Time"
        return ""
    display_time_difference.short_description = 'Time'

admin.site.register(Project, ProjectAdmin)
