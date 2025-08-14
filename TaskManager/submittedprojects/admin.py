# submittedproject/admin.py

from django.contrib import admin
from .models import SubmittedProjects

@admin.register(SubmittedProjects)
class SubmittedProjectAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'title',
        'hours_assigned',
        'tracked_time',
        'get_time_difference',
        'get_status',
        'submitted_at',
    )
    list_filter = ('user',)

    def get_time_difference(self, obj):
        return f"{obj.time_difference()} hrs"
    get_time_difference.short_description = 'Time +/-'

    def get_status(self, obj):
        return obj.status()
    get_status.short_description = 'Status'


from django.contrib import admin
from .models import SubmittedProjects

# Make sure they are not registered, or unregister them
admin.site.unregister(SubmittedProjects)
