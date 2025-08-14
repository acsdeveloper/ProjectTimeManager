# IMP MODULES

from datetime import timedelta
from collections import defaultdict
from django.utils.timezone import now
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Task, TaskTimer, WorkSession




# ─── Utility to calculate total worked hours ────────────────────────────────
def get_user_work_summary(user):
    sessions = WorkSession.objects.filter(user=user)

    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_year = today.replace(month=1, day=1)

    daily = timedelta()
    weekly = timedelta()
    yearly = timedelta()

    for session in sessions:
        duration = session.duration or timedelta()
        if session.start_time.date() == today:
            daily += duration
        if session.start_time.date() >= start_of_week:
            weekly += duration
        if session.start_time.date() >= start_of_year:
            yearly += duration

    def format_timedelta(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    return {
        "daily": format_timedelta(daily),
        "weekly": format_timedelta(weekly),
        "yearly": format_timedelta(yearly)
    }

# ─── Inline Task display under User ─────────────────────────────────────────
class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    show_change_link = True

# ─── Final CustomUserAdmin ──────────────────────────────────────────────────
class CustomUserAdmin(BaseUserAdmin):
    inlines = [TaskInline]

    readonly_fields = BaseUserAdmin.readonly_fields + ('total_hours_worked', 'work_history',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Work Stats', {
            'fields': ('total_hours_worked', 'work_history'),
        }),
    )

    def total_hours_worked(self, obj):
        summary = get_user_work_summary(obj)
        return format_html(
            "<div style='margin:20px 0; padding:10px; background:#222; border:1px solid #444;'>"
            "<h3 style='color:#4ec9b0;'>Total Hours Worked</h3>"
            "<ul>"
            "<li><strong>Today:</strong> {}</li>"
            "<li><strong>This Week:</strong> {}</li>"
            "<li><strong>This Year:</strong> {}</li>"
            "</ul>"
            "</div>",
            summary['daily'],
            summary['weekly'],
            summary['yearly']
        )

    def work_history(self, obj):
        sessions = WorkSession.objects.filter(user=obj).order_by('start_time')
        
        history = defaultdict(timedelta)
        for session in sessions:
            date = session.start_time.date()
            history[date] += session.duration or timedelta()

        rows = ""
        for date, td in sorted(history.items(), reverse=True):  # Most recent first
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
            rows += f"<tr><td>{date}</td><td>{formatted}</td></tr>"

        return format_html(
            "<div style='margin: 20px 0;'>"
            "<h3 style='color:#4ec9b0;'>Work History (by Date)</h3>"
            "<table style='border-collapse: collapse; width: 100%;'>"
            "<thead><tr style='background-color: #444; color: white;'>"
            "<th style='padding: 8px; border: 1px solid #555;'>Date</th>"
            "<th style='padding: 8px; border: 1px solid #555;'>Total Time</th>"
            "</tr></thead>"
            "<tbody>{}</tbody>"
            "</table></div>",
            format_html(rows)
        )

# Register Custom User Admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ─── TaskTimer Inline inside Task ───────────────────────────────────────────
class TaskTimerInline(admin.TabularInline):
    model = TaskTimer
    extra = 0
    show_change_link = True
    readonly_fields = ('formatted_tracked_time',)
    fields = (
        'start_time', 'pause_time', 'resume_time', 'end_time',
        'formatted_tracked_time', 'pause_count', 'resume_count', 'status'
    )

    def formatted_tracked_time(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return "—"

from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from datetime import timedelta
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Task, TaskTimer, WorkSession


# ─── Inline for TaskTimer ─────────────────────────────────────────────
class TaskTimerInline(admin.TabularInline):
    model = TaskTimer
    extra = 0
    show_change_link = False
    can_delete = False
    readonly_fields = (
        'start_time', 'pause_time', 'resume_time', 'end_time',
        'formatted_tracked_time', 'pause_count', 'resume_count', 'status'
    )
    fields = (
        'start_time', 'pause_time', 'resume_time', 'end_time',
        'formatted_tracked_time', 'pause_count', 'resume_count', 'status'
    )

    def formatted_tracked_time(self, obj):
        if obj.start_time and obj.end_time:
            td = obj.end_time - obj.start_time
            total_seconds = int(td.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return "00:00:00"

    formatted_tracked_time.short_description = "Tracked Time"


# ─── Task Admin ───────────────────────────────────────────────────────
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskTimerInline]
    readonly_fields = ['task_completion_summary']
    list_display = ['title', 'is_submitted', 'submitted_at']
    list_filter = ('is_submitted', 'deadline', 'user')
    search_fields = ('title', 'user__username')

    def tracking_info(self, obj):
        total_seconds = self.get_total_seconds_for_task(obj)
        formatted_time = self.format_seconds_to_hms(total_seconds)
        assigned_hours = obj.hours_assigned or "Not Assigned"

        return format_html(
            '<div style="padding: 10px;">'
            '<b>⏱ Total Time Worked:</b> {}<br>'
            '<b>📌 Assigned Hours:</b> {} hours<br>'
            '</div>',
            formatted_time,
            assigned_hours
        )

    def get_total_seconds_for_task(self, obj):
        sessions = obj.work_sessions.all()
        total = sum((s.duration.total_seconds() for s in sessions if s.duration), 0)
        return int(total)

    def format_seconds_to_hms(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def task_completion_summary(self, obj):
        from .models import WorkSession  # Safe local import
        sessions = WorkSession.objects.filter(task=obj).select_related('user')

        user_sessions = {}
        for session in sessions:
            user = session.user.username
            if user not in user_sessions:
                user_sessions[user] = []
            user_sessions[user].append(session)

        assigned = float(obj.hours_assigned or 0)

        html = """
        <h3 style="margin-top:20px;">📊 User Completion Summary</h3>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ccc; background: #222; color: #eee;">
            <thead>
                <tr style="background-color:#333;">
                    <th>User</th>
                    <th>Assigned Hours</th>
                    <th>Time Taken</th>
                    <th>Submitted At</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """

        for user, sessions in user_sessions.items():
            tracked_seconds = sum((s.duration.total_seconds() for s in sessions if s.duration), 0)
            tracked_hours = tracked_seconds / 3600

            start = min(s.start_time for s in sessions)
            end = max(s.end_time for s in sessions)
            time_taken = end - start
            time_taken_str = str(time_taken).split('.')[0]

            submitted_at = obj.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if obj.is_submitted and obj.submitted_at else 'Not Submitted'
            status = "✅ Early" if tracked_hours <= assigned else "❌ Overtime"

            html += f"""
                <tr>
                    <td>{user}</td>
                    <td>{assigned:.2f}</td>
                    <td>{time_taken_str}</td>
                    <td>{submitted_at}</td>
                    <td>{status}</td>
                </tr>
            """

        html += "</tbody></table>"
        return mark_safe(html)




# ─── WorkSession Admin (Hidden from Homepage) ──────────────────────────────
@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'start_time', 'end_time', 'duration')
    list_filter = ('user', 'start_time')
    ordering = ('-start_time',)

    def has_module_permission(self, request):
        return False

# ─── TaskTimer Admin (Hidden from Homepage) ────────────────────────────────
@admin.register(TaskTimer)
class TaskTimerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'task', 'start_time', 'pause_time',
        'resume_time', 'end_time', 'status',
        'total_tracked_seconds', 'created_at'
    )
    list_filter = ('status', 'task')
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        return False
