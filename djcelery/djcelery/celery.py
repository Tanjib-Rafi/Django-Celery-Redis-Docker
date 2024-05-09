from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcelery.settings')

celery_app = Celery('djcelery')

celery_app.config_from_object('django.conf:settings', namespace='')

# Set the schedule filename for Celery Beat
celery_app.conf.beat_schedule_filename = 'celerybeat-schedule'

# Set the result backend for Celery Beat
celery_app.conf.broker_url = 'redis://redis:6379/0'

celery_app.conf.result_backend = 'redis://redis:6379/0'


# Discover and configure tasks in all installed apps
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    'update_cache_task': {
        'task': 'cache_search.tasks.update_cache',
        'schedule': 60.0,  # Every 60 seconds
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
