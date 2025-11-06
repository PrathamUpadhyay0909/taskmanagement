from __future__ import absolute_import

from celery import Celery
from django.conf import settings as celery_settings
from api import celery_schedule

app = Celery(

    broker=celery_settings.BROKER_URL,
    backend=celery_settings.CELERY_RESULT_BACKEND,
    include=['taskmanagement.tasks']
)

app.conf.update(
     CELERY_TASK_RESULT_EXPIRES=3600,
     CELERYBEAT_SCHEDULE=celery_schedule.CELERYBEAT_SCHEDULE
)

if __name__ == '__main__':
    app.start()
