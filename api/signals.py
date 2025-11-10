from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .tasks import send_task_assignment_email

@receiver(post_save, sender=Task)
def on_task_created_send_email(sender, instance: Task, created, **kwargs):
    if created:
        send_task_assignment_email.delay(instance.id)
