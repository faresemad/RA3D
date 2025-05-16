import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.sellers.models import SellerRequest
from apps.users.models import CustomUserProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SellerRequest)
def update_user_status_to_pending(sender, instance: SellerRequest, created, **kwargs):
    if created:
        logger.info("Updating user status to pending")
        instance.user.status = CustomUserProfile.AccountStatus.PENDING_SELLER
        instance.user.save()
