from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.loginAccess, name='loginAccess'),  # Custom login page
    # ✅ Use only this logout path
    path('logout/', views.logout_view, name='logout'),
    # Task Manager Views
    path('home/', views.home, name='home'),
    path('create/', views.create_task, name='create_task'),
    path('update/<int:pk>/', views.update_task, name='update_task'),
    path('delete/', views.delete_tasks, name='delete_tasks'),
    path('timer/<str:action>/<int:task_id>/', views.task_timer_event, name='task_timer_event'),
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),
    path('frontend/login/', views.frontend_login, name='frontend_login'),
    path('frontend/logout/', views.frontend_logout, name='frontend_logout'),
    path('frontend/dashboard/', views.frontend_dashboard, name='frontend_dashboard'),
    # path('export-tasks/', views.export_task_details_to_sheet),
    # Admin Auth
    path('auth/logout/', views.logout_view, name='logout_view'),
]
from social_django import views as social_views
from django.views.defaults import permission_denied

handler403 = 'tasks.views.custom_auth_cancelled'
handler403 = 'tasks.views.custom_auth_denied'

