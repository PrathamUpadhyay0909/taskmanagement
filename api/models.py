from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
)

def default_deadline():
    return timezone.now() + timedelta(days=7)

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ManyToManyField(User, related_name='tasks')
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateTimeField(default=default_deadline)
    remark = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (#{self.id})"

class ManagerProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    name = models.CharField(max_length=100, blank=True, null=True)  
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name or self.user.username} (Manager)"  

class EmployeeProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    name = models.CharField(max_length=100, blank=True, null=True)  
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name or self.user.username} (Employee)"  
