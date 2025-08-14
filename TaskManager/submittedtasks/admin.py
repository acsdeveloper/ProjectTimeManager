from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Sum
from django.utils.html import format_html
from datetime import timedelta

from .models import SubmittedTask
from tasks.models import WorkSession

# 🔍 Filter to check if task is shared by multiple users
class MultiUserFilter(SimpleListFilter):
    title = 'Multiple Users?'
    parameter_name = 'multi_user'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes (Multiple Users)'),
            ('no', 'No (Single User)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            task_ids = (
                WorkSession.objects
                .values('task')
                .annotate(user_count=Count('user', distinct=True))
                .filter(user_count__gt=1)
                .values_list('task', flat=True)
            )
            return queryset.filter(id__in=task_ids)

        if self.value() == 'no':
            task_ids = (
                WorkSession.objects
                .values('task')
                .annotate(user_count=Count('user', distinct=True))
                .filter(user_count=1)
                .values_list('task', flat=True)
            )
            return queryset.filter(id__in=task_ids)

        return queryset

# ✅ Admin panel for submitted tasks
@admin.register(SubmittedTask)
class SubmittedTaskAdmin(admin.ModelAdmin):
    list_display = (
        'get_usernames',
        'get_task_title',
        'get_assigned_hours',
        'get_completed_hours',
        'get_difference',
        'get_status',
    )
    ordering = ('submitted_at',)
    list_filter = (MultiUserFilter,)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_submitted=True)

    def get_usernames(self, obj):
        users = WorkSession.objects.filter(task=obj).values_list('user__username', flat=True).distinct()
        count = len(users)
        if count == 1:
            return format_html('<span style="color:blue;">👤 {}</span>', users[0])
        elif count > 1:
            return format_html('<span style="color:purple;">👥 {}</span>', ', '.join(users))
        return format_html('<span style="color:gray;">—</span>')
    get_usernames.short_description = 'Users Working'

    def get_task_title(self, obj):
        return obj.title
    get_task_title.short_description = 'Task Title'

    def get_assigned_hours(self, obj):
        seconds = int((obj.hours_assigned or 0) * 3600)
        return str(timedelta(seconds=seconds))
    get_assigned_hours.short_description = 'Assigned Time'

    def get_completed_hours(self, obj):
        total = WorkSession.objects.filter(task=obj).aggregate(total=Sum('duration'))['total']
        if total:
            seconds = int(total.total_seconds())
            return str(timedelta(seconds=seconds))
        return "00:00:00"
    get_completed_hours.short_description = 'Completed Time'

    def get_difference(self, obj):
        assigned = float(obj.hours_assigned or 0)
        total = WorkSession.objects.filter(task=obj).aggregate(total=Sum('duration'))['total']

        assigned_seconds = int(assigned * 3600)

        if total:
            completed_seconds = int(total.total_seconds())
            diff_seconds = completed_seconds - assigned_seconds
            sign = '-' if diff_seconds > 0 else 'Available ' if diff_seconds < 0 else ''
            formatted = str(timedelta(seconds=abs(diff_seconds)))
            return f"{sign}{formatted}"

        return f"-{str(timedelta(seconds=assigned_seconds))}"
    get_difference.short_description = 'Time'

    def get_status(self, obj):
        return format_html('<span style="color:green;">✅ Done</span>')
    get_status.short_description = 'Status'
