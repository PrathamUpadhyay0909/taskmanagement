from django.urls import path
from .views import (
    RegisterView, LoginView,ManagerTaskListCreateView, ManagerTaskDetailView,EmployeeMyTasksView, EmployeeTaskStatusUpdateView,
)

urlpatterns = [
    path("register/",RegisterView.as_view(),name="register"),
    path("login/",LoginView.as_view(),name="login"),
    path("tasks/",ManagerTaskListCreateView.as_view(),name="tasks"),
    path("tasks/<int:pk>/",ManagerTaskDetailView.as_view(),name="task-detail"),
    path("my-tasks/",EmployeeMyTasksView.as_view(),name="my-tasks"),
    path("my-tasks/<int:pk>/status/",EmployeeTaskStatusUpdateView.as_view(),name="my-task-status"),
]


# | **Redis**         | Use Memurai (installed on Windows)                            
# | **Celery Worker** | celery -A taskmanagement worker --pool=solo --loglevel=info 
# | **Celery Beat**   | celery -A taskmanagement beat --loglevel=info             
# | **Django Server** | python manage.py runserver                                  

