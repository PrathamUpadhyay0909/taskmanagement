from datetime import timedelta

CELERYBEAT_SCHEDULE = {
     'add-every-30-seconds': {
          'task': 'tasks.add',
          'schedule': timedelta(seconds=3),
          'args': (16, 16)
     },
 }