import os

from celery import Celery
from celery.beat import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("Ra3d")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cancel-expired-orders": {
        "task": "apps.orders.tasks.cancel_expired_orders",
        "schedule": crontab(minute="*/15"),
    },
    "delete-expired-orders": {
        "task": "apps.orders.tasks.delete_expired_orders",
        "schedule": crontab(hour=0, minute=0),
    },
    "release-expired-reservations": {
        "task": "apps.orders.tasks.release_expired_reservations",
        "schedule": crontab(minute="*/5"),
    },
}
