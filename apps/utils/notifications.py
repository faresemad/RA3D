import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def send_notification(
    user,
    message,
    url=None,
    category=Notification.NotificationType.SYSTEM,
    priority=Notification.NotificationPriority.NORMAL,
    expiration=None,
    action_required=False,
):
    """
    Send an advanced notification to a user.

    Args:
        user (User): The user to receive the notification.
        message (str): The notification message.
        url (str, optional): The URL associated with the notification.
        category (str, optional): The category of the notification (e.g., 'system', 'user').
        priority (str, optional): The priority of the notification (e.g., 'low', 'high').
        expiration (datetime, optional): The expiration date of the notification.

    Returns:
        Notification: The created notification object.
    """
    if url is None:
        url = settings.HOST
    if url and not url.startswith(("http://", "https://")):
        try:
            url = reverse(url)
        except Exception as e:
            logger.error(f"Error generating URL from reverse: {e}")
            url = f"{settings.HOST}{url}"
    logger.info(f"URL generated from reverse: {url}")
    notification = Notification.objects.create(
        user=user,
        message=message,
        url=url,
        category=category,
        priority=priority,
        expiration=expiration,
        action_required=action_required,
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
                "url": notification.url,
                "category": notification.category,
                "priority": notification.priority,
                "expiration": notification.expiration.isoformat() if notification.expiration else None,
                "action_required": notification.action_required,
            },
        },
    )

    return notification


def mark_notification_as_read(notification_id):
    """
    Mark a notification as read.

    Args:
        notification_id (UUID): The ID of the notification to mark as read.

    Returns:
        bool: True if the notification was successfully marked as read, False otherwise.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        logger.info("Marking notification as read")
        return True
    except Notification.DoesNotExist:
        logger.exception("Notification not found")
        return False


def delete_expired_notifications():
    """
    Delete all expired notifications.

    Returns:
        int: The number of deleted notifications.
    """
    now = timezone.now()
    expired_notifications = Notification.objects.filter(expiration__lte=now)
    count = expired_notifications.count()
    expired_notifications.delete()
    logger.info("Deleting expired notifications")
    return count
