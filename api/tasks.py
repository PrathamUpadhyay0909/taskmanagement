from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Task
from django.utils import timezone
from datetime import timedelta
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from __future__ import absolute_import

@shared_task
def send_task_assignment_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        assigned_user = task.assigned_to
        created_by = task.created_by
        subject = f"New Task Assigned - {task.title}"
        message = f"""Hello {assigned_user.username},
        You have been assigned a new task by {created_by.username}.
        Task Title: {task.title}
        Description: {task.description}
        Deadline: {task.deadline}
        """
        send_mail(
            subject,
            message,
            [assigned_user.email],
            fail_silently=False,

        )
    except Task.DoesNotExist:
        pass

@shared_task
def send_task_deadline_reminder():
    upcoming_deadline = timezone.now() + timedelta(days=1)
    tasks = Task.objects.filter(deadline__lte=upcoming_deadline, status__in=['pending', 'in_progress'])
    for task in tasks:
        assigned_user = task.assigned_to
        subject = f"Task Deadline Reminder - {task.title}"
        message = f"""Hello {assigned_user.username},
        This is a reminder that the deadline for the task '{task.title}' is approaching on {task.deadline}.
        Please ensure that you complete the task on time.
        """
        send_mail(
            subject,
            message,
            [assigned_user.email],
            fail_silently=False,
        )  