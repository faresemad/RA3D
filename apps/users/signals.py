import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import CustomUserProfile
from apps.wallet.models import Wallet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUserProfile)
def create_wallet_for_new_user(
    sender: type[CustomUserProfile], instance: CustomUserProfile, created: bool, **kwargs
) -> None:
    """
    Create a wallet for a new user.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments

    Raises:
        ValidationError: If wallet creation fails
    """
    if not created:
        return

    user = instance
    logger.info(f"Initiating wallet creation for user: {user.email}")

    try:
        with transaction.atomic():
            # Check if wallet already exists
            if Wallet.objects.filter(user=user).exists():
                logger.warning(f"Wallet already exists for user: {user.email}")
                return

            wallet = Wallet.objects.create(user=user)
            logger.info(f"Wallet created successfully for user: {user.email} " f"(Wallet ID: {wallet.id})")

    except ValidationError as ve:
        logger.exception(f"Validation error creating wallet for {user.email}: {str(ve)}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error creating wallet for {user.email}: {str(e)}")
        raise
