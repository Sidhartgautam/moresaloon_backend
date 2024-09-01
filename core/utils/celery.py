from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-reminder-emails': {
        'task': 'your_app.tasks.send_appointment_confirmation',
        'schedule': timedelta(hours=1),  # Execute every hour
        'args': ('recipient@example.com', 'Reminder', 'Your appointment is coming up.'),
    },
}