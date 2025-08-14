from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    hours_assigned = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # New field to track total time
    tracked_time = models.DurationField(default=timedelta(), blank=True, null=True)

    def __str__(self):
        return self.title


class ProjectTimer(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timers')
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField(blank=True, null=True)

    def duration(self):
        if self.stopped_at:
            return self.stopped_at - self.started_at
        return timezone.now() - self.started_at
