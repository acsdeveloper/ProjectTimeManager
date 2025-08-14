from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime
import json
from django.contrib.auth import logout
from .models import Task, TaskTimer
from .forms import TaskForm
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task, WorkSession
from .utils import send_data_to_google_sheet, format_seconds_to_hms
from collections import defaultdict
from django.utils.timezone import now
from AssignTasks.models import AssignedTask
from .models import Task
from django.contrib.auth.models import User
from .utils import frontend_login_required


# VIEWS AND LOGIC FOR LOGIN
def loginAccess(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/auth/login/google-oauth2/')


@login_required(login_url='/auth/login/google-oauth2/')
def home(request):
    tasks = Task.objects.filter(user=request.user).order_by('-id')  # ✅ Fix applied

    if request.method == 'POST':
        selected_ids = request.POST.getlist('ids')
        if selected_ids:
            Task.objects.filter(id__in=selected_ids, user=request.user).delete()  # 🛡️ Secure delete
            messages.success(request, "Selected task(s) deleted successfully!")
            return redirect('home')

    return render(request, 'tasks/home.html', {'tasks': tasks})



# ✅ Create Task View (Requires Login)
@csrf_exempt
@login_required(login_url='/auth/login/google-oauth2/')
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # ✅ assign logged-in user
            task.save()
            messages.success(request, "Task added successfully!")
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'tasks/home.html', {'form': form})


@csrf_exempt
@login_required(login_url='/auth/login/google-oauth2/')
def update_task(request, pk):
    task = get_object_or_404(Task, id=pk)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')

        # ✅ Get hours_assigned from form
        hours = request.POST.get('hours_assigned')
        task.hours_assigned = float(hours) if hours else None

        # ✅ Parse deadline
        deadline_str = request.POST.get('deadline')
        if deadline_str:
            parsed = parse_datetime(deadline_str)
            if parsed and timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            task.deadline = parsed
        else:
            task.deadline = None

        task.save()
        return redirect('home')



# ✅ Delete Tasks via AJAX (Requires Login)


def delete_tasks(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        for task_id in ids:
            try:
                task = AssignedTask.objects.get(id=task_id)

                # First delete related WorkSessions
                WorkSession.objects.filter(task=task).delete()

                # Then delete the task
                task.delete()
            except AssignedTask.DoesNotExist:
                continue  # Skip if task not found

        return redirect('home')

@csrf_exempt
@login_required(login_url='/auth/login/google-oauth2/')
def submit_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            data = json.loads(request.body)

            # ✅ Get tracked time (in seconds) from frontend
            elapsed_time = int(data.get("tracked_time", 0))  # e.g. 3900 = 1 hr 5 min

            if elapsed_time == 0:
                return JsonResponse({"status": "error", "message": "Tracked time is zero."})

            duration = timedelta(seconds=elapsed_time)
            end_time = now()
            start_time = end_time - duration

            # ✅ Create WorkSession with tracked time
            WorkSession.objects.create(
                user=request.user,
                task=task,
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )

            # ✅ Mark task as submitted
            task.is_submitted = True
            task.submitted_at = now()
            task.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Task submitted successfully!',
                'submitted_at': task.submitted_at.strftime('%Y-%m-%d %H:%M')
            })
        

        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# ✅ Timer Event API (Requires Login)
@csrf_exempt
@login_required(login_url='/auth/login/google-oauth2/')
def task_timer_event(request, action, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            data = json.loads(request.body)
            current_time = timezone.now()
            timer = TaskTimer.objects.filter(task=task, status__in=['running', 'paused']).last()

            if action == 'start':
                TaskTimer.objects.create(task=task, start_time=current_time, status='running')

            elif action == 'pause' and timer:
                timer.pause_time = current_time
                timer.total_tracked_seconds += int((current_time - timer.start_time).total_seconds())
                timer.status = 'paused'
                timer.pause_count += 1
                timer.save()

            elif action == 'resume' and timer:
                timer.resume_time = current_time
                timer.start_time = current_time
                timer.status = 'running'
                timer.resume_count += 1
                timer.save()

            elif action == 'end' and timer:
                timer.end_time = current_time
                timer.total_tracked_seconds += int((current_time - timer.start_time).total_seconds())
                timer.status = 'ended'
                timer.save()

            elif action == 'reset':
                TaskTimer.objects.filter(task=task, status__in=['running', 'paused']).delete()

            return JsonResponse({'status': 'success', 'action': action})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def work_end(request):
    from django.utils.dateparse import parse_datetime
    from django.utils.timezone import make_aware
    import json

    data = json.loads(request.body)
    task_id = data['task_id']
    user_id = data['user_id']
    user = User.objects.get(id=user_id)
    end_time = make_aware(parse_datetime(data['end_time']))

    start_iso = request.session.get(f'task_{task_id}_start')
    if start_iso:
        start_time = parse_datetime(start_iso)
        start_time = make_aware(start_time)
        duration = end_time - start_time  # ✅ Calculate duration

        # ✅ Save to DB
        WorkSession.objects.create(
            user=user,
            task=Task.objects.get(id=task_id),
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )
        print(f"✅ Session created: {duration}")
    else:
        print("❌ Start time not found in session")

    return JsonResponse({'status': 'ended'})


def dashboard(request):
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user).order_by('-id')
        return render(request, 'dashboard.html', {'tasks': tasks})
    return redirect('login')


def custom_auth_denied(request, exception=None):
    return render(request, 'auth_denied.html', status=403)

def custom_auth_conflict(request, exception=None):
    return render(request, 'auth_conflict.html', status=409)


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@login_required
def user_work_summary(request):
    user = request.user

    # Task count
    completed_tasks = Task.objects.filter(user=user, is_submitted=True).count()

    # Work sessions
    sessions = WorkSession.objects.filter(user=user)
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_year = today.replace(month=1, day=1)

    summary = {
        "daily": timedelta(),
        "weekly": timedelta(),
        "yearly": timedelta()
    }

    history = defaultdict(timedelta)

    for session in sessions:
        duration = session.duration or timedelta()
        session_date = session.start_time.date()

        if session_date == today:
            summary["daily"] += duration
        if session_date >= start_of_week:
            summary["weekly"] += duration
        if session_date >= start_of_year:
            summary["yearly"] += duration

        history[session_date] += duration

    # Format durations
    formatted_summary = {k: format_timedelta(v) for k, v in summary.items()}
    formatted_history = {d.strftime('%Y-%m-%d'): format_timedelta(t) for d, t in sorted(history.items(), reverse=True)}

    context = {
        "completed_tasks": completed_tasks,
        "summary": formatted_summary,
        "history": formatted_history
    }

    return render(request, "user_work_summary.html", context)


# ================================
# FRONTEND AUTH VIEWS
# ================================

def frontend_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                request.session['frontend_user_id'] = user.id
                messages.success(request, "Logged in successfully!")
                return redirect('frontend_dashboard')
            else:
                messages.error(request, "Incorrect password.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, "frontend/login.html")


def frontend_logout(request):
    try:
        del request.session['frontend_user_id']
    except KeyError:
        pass
    return redirect('frontend_login')


@frontend_login_required
def frontend_dashboard(request):
    user_id = request.session.get('frontend_user_id')
    user = get_object_or_404(User, id=user_id)
    tasks = Task.objects.filter(user=user).order_by('-id')
    return render(request, 'frontend/dashboard.html', {'user': user, 'tasks': tasks})


@frontend_login_required
def frontend_dashboard(request):
    user_id = request.session.get('frontend_user_id')
    user = get_object_or_404(User, id=user_id)

    tasks = Task.objects.filter(user=user).order_by('-id')

    # ✅ Prepare tracked seconds per task
    tracked_seconds = {}
    for task in tasks:
        last_timer = TaskTimer.objects.filter(task=task).order_by('-id').first()
        tracked_seconds[task.id] = last_timer.total_tracked_seconds if last_timer else 0

    return render(request, 'frontend/dashboard.html', {
        'user': user,
        'tasks': tasks,
        'tracked_seconds': tracked_seconds,
    })


# 🧠 Helper function to format seconds into HH:MM:SS
def format_seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) % 60 // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) % 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) % 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# @csrf_exempt
# def export_task_details_to_sheet(request):
#     SHEET_ID = '1IfhspM4jn9r_luxbPq2U-qUTOD6oij62Z31_Y5wSig4'
#     rows = []

#     tasks = Task.objects.select_related('user').prefetch_related('timers')

#     for task in tasks:
#         total_seconds = sum(
#             t.total_tracked_seconds for t in task.timers.all() if t.total_tracked_seconds
#         )
#         total_time_formatted = format_seconds_to_hms(total_seconds)

#         timer = task.timers.last() if task.timers.exists() else None
#         pause_count = timer.pause_count if timer else 0
#         resume_count = timer.resume_count if timer else 0

#         if task.is_submitted:
#             if task.deadline and task.submitted_at > task.deadline:
#                 status = "❌ Submitted After Deadline"
#             else:
#                 status = "✅ Submitted On Time"
#         else:
#             status = "⏳ Not Submitted"

#         rows.append([
#             task.user.username,
#             task.title,
#             task.description or '',
#             task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else '—',
#             pause_count,
#             resume_count,
#             task.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if task.is_submitted else '—',
#             status,
#             total_time_formatted
#         ])

#     send_data_to_google_sheet(rows, SHEET_ID, worksheet_name='Sheet1')

#     return JsonResponse({'status': '✅ Task data exported to Google Sheets'})



