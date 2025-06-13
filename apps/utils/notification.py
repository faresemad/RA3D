import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def send_notification(
    user,
    message=None,
):
    """
    Send an advanced notification to a user.

    Args:
        user (User): The user to receive the notification.
        message (str): The notification message.

    Returns:
        Notification: The created notification object.
    """
    notification = Notification.objects.create(
        user=user,
        message=message,
    )
    logger.info(f"Sending notification: {notification}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send_notification",
            "notification": {
                "id": str(notification.id),
                "message": notification.message,
                "created_at": notification.created_at.isoformat(),
                "is_read": notification.is_read,
            },
        },
    )

    return notification
