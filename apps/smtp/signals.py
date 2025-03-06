import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.smtp.models import SMTP
from apps.smtp.tasks import get_domain_info

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SMTP)
def fetch_domain_info_after_creation(sender, instance: SMTP, created, **kwargs):
    """Trigger Celery task to fetch domain info after SMTP object is created."""
    if created:
        # Only trigger the task when a new SMTP object is created
        logger.info(f"Triggering fetch_domain_info task for domain: {instance.ip}")
        get_domain_info.apply_async((instance.id,))
