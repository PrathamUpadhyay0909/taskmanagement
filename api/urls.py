from django.urls import path
from .views import RegisterView, LoginView, TaskView, TaskDetailView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('my-tasks/', TaskView.as_view(), name='my-tasks'),
    path('my-tasks/<int:pk>/status/', TaskDetailView.as_view(), name='my-task-status')

]