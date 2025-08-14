
from django.contrib import admin
from django.urls import path, include
from AssignTasks import views  # ✅ Import from tasks app

# from .views import save_session


urlpatterns = [
    path('work_details/', views.work_details, name='work_details'),
]
