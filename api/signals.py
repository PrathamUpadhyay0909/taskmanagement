from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Task
from .tasks import send_task_assignment_email


@receiver(m2m_changed, sender=Task.assigned_to.through)
def on_task_assigned(sender, instance, action, **kwargs):
    if action == "post_add":
        send_task_assignment_email.delay(instance.id)
