# submittedtasks/models.py

from tasks.models import Task

class SubmittedTask(Task):
    class Meta:
        proxy = True
        verbose_name = "Submitted Task"
        verbose_name_plural = "Submitted Tasks"
        
        