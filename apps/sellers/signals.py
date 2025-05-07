from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.sellers.models import SellerRequest
from apps.users.models import CustomUserProfile


@receiver(post_save, sender=SellerRequest)
def create_seller_profile(sender, instance: SellerRequest, created, **kwargs):
    if created:
        user: CustomUserProfile = instance.user
        match instance.status:
            case SellerRequest.Status.PENDING:
                user.make_pending_seller()
            case (SellerRequest.Status.APPROVED):
                user.make_seller()
            case (SellerRequest.Status.REJECTED):
                user.make_buyer()
