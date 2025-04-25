import logging

from celery import shared_task

from apps.services.order import OrderServices

logger = logging.getLogger(__name__)
order_services = OrderServices()


@shared_task
def cancel_expired_orders():
    """
    Cancels orders that have expired using the order services.

    This Celery shared task runs the cancel_expired_orders method from OrderServices
    and logs a success message after cancellation.

    Task is designed to be triggered periodically to clean up and manage
    expired/stale orders in the system.
    """
    order_services.cancel_expired_orders()
    logger.info("Cancelled expired orders successfully.")


@shared_task
def delete_expired_orders():
    """
    Deletes expired orders using the order services.

    This Celery shared task runs the delete_expired_orders method from OrderServices
    and logs a success message after deletion.

    Task is designed to be triggered periodically to clean up and manage
    expired/stale orders in the system.
    """
    order_services.delete_expired_orders()
    logger.info("Deleted expired orders successfully.")
