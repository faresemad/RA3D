import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.rdp.models import Rdp
from apps.rdp.tasks import get_ip_geolocation_and_hosting_info

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Rdp)
def fetch_rdp_details_after_creation(sender, instance: Rdp, created, **kwargs):
    """Trigger Celery task to fetch RDP details after Rdp object is created."""
    if created:
        # Only trigger the task when a new Rdp object is created
        logger.info(f"Triggering fetch_rdp_details task for RDP IP: {instance.ip}")
        get_ip_geolocation_and_hosting_info.apply_async((instance.id,))
