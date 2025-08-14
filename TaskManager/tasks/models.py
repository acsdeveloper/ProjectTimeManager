# tasks/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from AssignTasks.models import AssignedTask


# MODEL FOR THE TASKS TO CREATE AND TO ADD IN THE DATABASE
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Link to User
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    hours_assigned = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Optional helper method
    def get_hours_assigned(self):
        return self.hours_assigned

    @property
    def is_overdue(self):
        if self.deadline:
            return timezone.localtime(timezone.now()) > timezone.localtime(self.deadline)
        return False

    def get_total_seconds(self):
        total = self.work_sessions.aggregate(total=models.Sum('duration'))['total']
        return int(total.total_seconds()) if total else 0

    def get_pause_count(self):
        # Assuming 1 pause per WorkSession, unless you track it separately
        return self.work_sessions.count()

    def get_resume_count(self):
        # Assuming 1 resume per WorkSession, unless tracked separately
        return self.work_sessions.count()

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class TaskTimer(models.Model):
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('ended', 'Ended'),
    ]

    # task = models.ForeignKey('Task', related_name='task_timers', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="work_sessions")
    start_time = models.DateTimeField()
    pause_time = models.DateTimeField(null=True, blank=True)
    resume_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField()
    pause_count = models.IntegerField(default=0)
    resume_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def tracked_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta()

    @property
    def total_tracked_seconds(self):
        return int(self.tracked_time.total_seconds())

    def formatted_tracked_time(self):
        td = self.tracked_time
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    formatted_tracked_time.short_description = "Tracked Time (H:M:S)"

    def __str__(self):
        return f"Task #{self.task.id} - {self.task.title} ({self.status})"


class WorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # task = models.ForeignKey(AssignedTask, on_delete=models.CASCADE)
    # in WorkSession model
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField()

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} | {self.task.task_title} | {self.start_time.strftime('%Y-%m-%d %H:%M')} → {self.end_time.strftime('%H:%M')}"

    def __str__(self):
        return f"{self.user.username} | {self.start_time.strftime('%Y-%m-%d %H:%M')} → {self.end_time.strftime('%H:%M')}"

def get_summary_by_period(self):
    from .models import WorkSession  # adjust if necessary

    periods = {
        'Today': timezone.now().date(),
        'This Week': timezone.now() - timedelta(days=timezone.now().weekday()),
        'This Month': timezone.now().replace(day=1),
        'This Year': timezone.now().replace(month=1, day=1),
    }
    summary = {}

    for label, start_date in periods.items():
        sessions = self.work_sessions.filter(start_time__date__gte=start_date)
        per_user = {}

        for session in sessions:
            user = session.user.username
            duration = session.duration.total_seconds() / 3600  # convert to hours
            per_user.setdefault(user, 0)
            per_user[user] += duration

        summary[label] = per_user

    return summary
