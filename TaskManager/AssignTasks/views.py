from django.shortcuts import render
from AssignTasks.models import AssignedTask  # 👈 import the model

def work_details(request):
    task_list = AssignedTask.objects.filter(users=request.user)
    return render(request, 'tasks/work_details.html', {'task_list': task_list})


