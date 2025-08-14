# submittedproject/models.py

from django.db import models
from django.contrib.auth.models import User

class SubmittedProjects(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    hours_assigned = models.FloatField()
    tracked_time = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def time_difference(self):
        return round(self.tracked_time - self.hours_assigned, 2)

    def status(self):
        if self.time_difference() > 0:
            return f"⏱ Exceeded by {self.time_difference()} hrs"
        elif self.time_difference() < 0:
            return f"✅ Saved {abs(self.time_difference())} hrs"
        else:
            return "✅ On Time"

    def __str__(self):
        return f"{self.title} - {self.user.username}"
