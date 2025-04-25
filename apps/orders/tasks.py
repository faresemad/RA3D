import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.orders.models import Order, OrderStatus

logger = logging.getLogger(__name__)


@shared_task
def cancel_expired_orders():
    """
    Cancels orders that have exceeded their expiration time.

    This Celery task finds all pending orders that have been created longer than the defined
    expiration time and automatically changes their status to CANCELLED. Each cancelled order
    is logged for tracking purposes.

    Runs periodically to clean up and manage order lifecycle.
    """
    expiration_time = timezone.now() - timedelta(minutes=Order.EXPIRATION_MINUTES)
    expired_orders = Order.objects.filter(status=OrderStatus.PENDING, created_at__lt=expiration_time)

    for order in expired_orders:
        order.status = OrderStatus.CANCELLED
        order.save()
        logger.info(f"Canceled expired order {order.id}")
