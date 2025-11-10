from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Task


@shared_task
def send_task_assignment_email(task_id: int):
    try:
        task = (
            Task.objects
            .select_related("created_by")
            .prefetch_related("assigned_to")
            .get(id=task_id)
        )
    except Task.DoesNotExist:
        return

    created_by = task.created_by
    assigned_users = task.assigned_to.all()  

    subject = f"New Task Assigned - {task.title}"

    for user in assigned_users:
        message = (
            f"Hello {user.username},\n\n"
            f"You have been assigned a new task by {created_by.username}.\n\n"
            f"Task Title: {task.title}\n"
            f"Description: {task.description}\n"
            f"Deadline: {timezone.localtime(task.deadline).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Please complete it on time.\n\n"
            f"Regards,\nTask Management System"
        )
        send_mail(subject, message, None, [user.email], fail_silently=False)


@shared_task
def send_deadline_reminder_email(task_id: int):

    try:
        task = (
            Task.objects
            .select_related("created_by")
            .prefetch_related("assigned_to")
            .get(id=task_id)
        )
    except Task.DoesNotExist:
        return

    if task.status == "completed":
        return

    subject = f"Reminder - Task Deadline Approaching ({task.title})"
    deadline_str = timezone.localtime(task.deadline).strftime("%Y-%m-%d %H:%M:%S")

    for user in task.assigned_to.all():
        message = (
            f"Hello {user.username},\n\n"
            f"This is a reminder that your task \"{task.title}\" is due soon.\n"
            f"Deadline: {deadline_str}\n\n"
            f"Please make sure to complete it on time.\n\n"
            f"Regards,\nTask Management System"
        )
        send_mail(subject, message, None, [user.email], fail_silently=False)

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
