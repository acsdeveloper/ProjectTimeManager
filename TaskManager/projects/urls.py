from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),  # This maps to /projects/
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/start/', views.start_project_timer, name='start_project_timer'),
    path('projects/<int:project_id>/stop/', views.stop_project_timer, name='stop_project_timer'),
   # urls.py
    path('submit-project/<int:project_id>/', views.submit_project, name='submit_project'),
    # path('assigned/', assigned_projects_view, name='assigned_projects'),

]
