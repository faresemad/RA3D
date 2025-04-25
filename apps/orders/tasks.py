import logging

from celery import shared_task

from apps.services.order import OrderServices
from apps.services.transaction import TransactionService

logger = logging.getLogger(__name__)
order_services = OrderServices()
transaction_services = TransactionService()


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


@shared_task
def update_transaction_status(transaction_id: str, mapped_status: str):
    """
    Updates the status of a transaction using the transaction services.

    This Celery shared task runs the update_transaction_status method from TransactionService
    and logs a success message after the update.

    Args:
        transaction_id (str): The ID of the transaction to update
        mapped_status (str): The new status to set for the transaction
    """
    transaction_services.update_transaction_status(transaction_id, mapped_status)
    logger.info(f"Updated transaction {transaction_id} status to {mapped_status} successfully.")
