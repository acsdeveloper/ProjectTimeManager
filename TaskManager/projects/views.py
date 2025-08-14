from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages

from django.contrib.auth.decorators import login_required

@login_required
def projects(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tasks/projects.html', {'projects': projects})

from django.utils import timezone

@property
def is_overdue(self):
    return self.deadline and timezone.now() > self.deadline and not self.is_submitted


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Project
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from django.utils.timezone import now

@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        hours_assigned = request.POST.get('hours_assigned')

        Project.objects.create(
            user=request.user,
            title=title,
            description=description,
            deadline=deadline or None,
            hours_assigned=hours_assigned or 0
        )
        messages.success(request, 'Project created successfully.')
        return redirect('projects')  # make sure this matches your URL name
    return render(request, 'projects/projects.html')  # ✅ use correct path



from .models import Project, ProjectTimer
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def start_project_timer(request, project_id):
    project = Project.objects.get(id=project_id, user=request.user)
    ProjectTimer.objects.create(project=project, started_at=now())
    return JsonResponse({'status': 'started'})



@csrf_exempt
@login_required
def stop_project_timer(request, project_id):
    project = Project.objects.get(id=project_id, user=request.user)
    timer = project.timers.filter(stopped_at__isnull=True).last()
    if timer:
        timer.stopped_at = now()
        timer.save()

        # Update project's total time
        project.total_time_tracked += timer.duration()
        project.save()

    return JsonResponse({'status': 'stopped'})

from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from .models import Project
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
@login_required
def submit_project(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, user=request.user)

            tracked_time = request.POST.get('tracked_time')  # Expected "HH:MM:SS"
            print("Tracked time received:", tracked_time)

            if not tracked_time:
                return JsonResponse({'success': False, 'message': 'No tracked time provided.'})

            try:
                h, m, s = map(int, tracked_time.split(':'))
                delta = timedelta(hours=h, minutes=m, seconds=s)

                project.tracked_time = delta
                project.is_submitted = True  # ✅ Mark as submitted
                project.submitted_at = timezone.now()  # ✅ Record submission time
                project.save()

                print("Tracked time saved:", delta)
            except ValueError as e:
                print("Error parsing tracked_time:", e)
                return JsonResponse({'success': False, 'message': 'Invalid time format.'})

            return redirect('projects')

        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Project not found.'})








# @csrf_exempt
# @login_required
# def submit_project(request, project_id):
#     if request.method == 'POST':
#         try:
#             project = Project.objects.get(id=project_id, user=request.user)

#             tracked_time = request.POST.get('tracked_time')

#             if not tracked_time:
#                 messages.error(request, 'No tracked time provided.')
#                 return redirect('projects')

#             # Convert string to timedelta
#             try:
#                 h, m, s = map(int, tracked_time.split(":"))
#                 duration = timedelta(hours=h, minutes=m, seconds=s)
#             except Exception:
#                 messages.error(request, 'Invalid time format.')
#                 return redirect('projects')

#             project.tracked_time = duration
#             project.is_submitted = True
#             project.submitted_at = timezone.now()
#             project.save()

#             messages.success(request, 'Project submitted successfully!')
#             return redirect('projects')

#         except Project.DoesNotExist:
#             messages.error(request, 'Project not found.')
#             return redirect('projects')







# @csrf_exempt
# @login_required
# def submit_project(request, project_id):
#     if request.method == 'POST':
#         try:
#             project = Project.objects.get(id=project_id, user=request.user)

#             tracked_time = request.POST.get('tracked_time')  # ✅ from form POST

#             if not tracked_time:
#                 return JsonResponse({'success': False, 'message': 'No tracked time provided.'})

#             project.tracked_time = tracked_time
#             project.is_submitted = True
#             project.submitted_at = timezone.now()
#             project.save()

#             return JsonResponse({'success': True, 'message': 'Project submitted successfully!'})
#         except Project.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Project not found.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})









