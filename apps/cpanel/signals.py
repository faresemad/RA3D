import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.cpanel.models import CPanel
from apps.cpanel.tasks import get_domain_info

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CPanel)
def fetch_domain_info_after_creation(sender, instance: CPanel, created, **kwargs):
    """Trigger Celery task to fetch domain info after CPanel object is created."""
    if created:
        # Only trigger the task when a new CPanel object is created
        logger.info(f"Triggering fetch_domain_info task for domain: {instance.host}")
        get_domain_info.apply_async((instance.id,))
