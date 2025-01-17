import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shells.models import Shell
from apps.shells.tasks import fetch_shell_details

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Shell)
def fetch_shell_details_after_creation(sender, instance: Shell, created, **kwargs):
    """Trigger Celery task to fetch shell details after Shell object is created."""
    if created:
        # Only trigger the task when a new Shell object is created
        logger.info(f"Triggering fetch_shell_details task for Shell URL: {instance.shell_url}")
        fetch_shell_details.apply_async((instance.id,))
