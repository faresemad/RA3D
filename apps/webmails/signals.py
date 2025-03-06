import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.webmails.models import WebMail
from apps.webmails.tasks import get_domain_info

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WebMail)
def fetch_domain_info_after_creation(sender, instance: WebMail, created, **kwargs):
    """Trigger Celery task to fetch domain info after WebMail object is created."""
    if created:
        # Only trigger the task when a new WebMail object is created
        logger.info(f"Triggering fetch_domain_info task for domain: {instance.domain}")
        get_domain_info.apply_async((instance.id,))
