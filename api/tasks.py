from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .models import Task

@shared_task
def send_task_assignment_email(task_id: int):
    try:
        task = Task.objects.select_related("assigned_to", "created_by").get(id=task_id)
    except Task.DoesNotExist:
        return

    assigned_user = task.assigned_to
    created_by = task.created_by

    subject = f"New Task Assigned - {task.title}"
    message = (
        f"Hello {assigned_user.username},\n\n"
        f"You have been assigned a new task by {created_by.username}.\n\n"
        f"Task Title: {task.title}\n"
        f"Description: {task.description}\n"
        f"Deadline: {timezone.localtime(task.deadline)}\n"
    )

    send_mail(subject, message, None, [assigned_user.email], fail_silently=False)


@shared_task
def send_deadline_reminder_email(task_id: int):
    try:
        task = Task.objects.select_related("assigned_to").get(id=task_id)
    except Task.DoesNotExist:
        return

    if task.status == "completed":
        return

    subject = "Reminder - Task Deadline Approaching"
    message = (
        f"Hello {task.assigned_to.username},\n\n"
        f"Your task \"{task.title}\" is due in 5 minutes.\n"
        f"Please make sure to complete it on time.\n"
        f"Deadline: {timezone.localtime(task.deadline)}\n"
    )
    send_mail(subject, message, None, [task.assigned_to.email], fail_silently=False)
    task.reminder_sent = True
    task.save(update_fields=["reminder_sent"])


@shared_task
def check_and_send_deadline_reminders():
    now = timezone.now()
    lookahead = now + timedelta(minutes=5)
    qs = Task.objects.filter(
        reminder_sent=False,
        status__in=["pending", "in_progress"],
        deadline__lte=lookahead,
        deadline__gte=now,
    )
    for task in qs:
        send_deadline_reminder_email.delay(task.id)
