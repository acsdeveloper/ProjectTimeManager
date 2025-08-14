# tasks/models.py

from django.db import models
from django.contrib.auth.models import User

class AssignedTask(models.Model):
    users = models.ManyToManyField(User, related_name='assigned_tasks')
    task_title = models.CharField(max_length=255)
    task_description = models.TextField()
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    hours_assigned = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.task_title
