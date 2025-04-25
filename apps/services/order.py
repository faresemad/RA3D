import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Account
from apps.cpanel.models import CPanel
from apps.orders.models import Order, OrderStatus
from apps.rdp.models import Rdp
from apps.shells.models import Shell
from apps.smtp.models import SMTP
from apps.webmails.models import WebMail

logger = logging.getLogger(__name__)


class OrderServices:
    """
    Provides service methods for managing orders in the system.

    This class contains static methods for handling order-related operations such as:
    - Cancelling expired orders
    - Marking items as sold
    - Retrieving unsold items
    - Managing user orders
    - Cancelling specific orders
    - Fetching orders by ID

    The methods handle various order statuses and perform database operations with logging.
    """

    EXPIRATION_MINUTES = 15

    @staticmethod
    def cancel_expired_orders():
        """
        Cancels orders that have remained in a pending status beyond the configured expiration time.

        This method identifies and updates pending orders that have exceeded the predefined
        expiration duration (EXPIRATION_MINUTES). Each expired order is marked as cancelled
        and logged for tracking purposes.

        The method performs the following actions:
        - Calculates the expiration threshold based on current time and EXPIRATION_MINUTES
        - Retrieves all pending orders created before the expiration time
        - Updates each expired order's status to CANCELLED
        - Logs information about each cancelled order
        """
        expiration_time = timezone.now() - timedelta(minutes=OrderServices.EXPIRATION_MINUTES)
        expired_orders = Order.objects.filter(status=OrderStatus.PENDING, created_at__lt=expiration_time)
        for order in expired_orders:
            order.status = OrderStatus.CANCELLED
            order.save()
            logger.info(f"Cancelled expired order: {order.id}")

    @staticmethod
    def mark_items_as_sold(order: Order):
        """
        Marks the ordered items (account, cpanel, rdp, etc.) as sold or not available anymore.
        This should be called when order is completed.
        """
        if order.account:
            order.account.mark_as_sold()
        if order.cpanel:
            order.cpanel.mark_as_sold()
        if order.rdp:
            order.rdp.mark_as_sold()
        if order.shell:
            order.shell.mark_as_sold()
        if order.smtp:
            order.smtp.mark_as_sold()
        if order.webmail:
            order.webmail.mark_as_sold()

        logger.info(f"Marked items as sold for order {order.id}")

    @staticmethod
    def get_unsold_items():
        return {
            "accounts": Account.objects.filter(is_sold=False),
            "cpanels": CPanel.objects.filter(is_sold=False),
            "rdps": Rdp.objects.filter(is_sold=False),
            "shells": Shell.objects.filter(is_sold=False),
            "smtps": SMTP.objects.filter(is_sold=False),
            "webmails": WebMail.objects.filter(is_sold=False),
        }

    @staticmethod
    def get_user_orders(user):
        return Order.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order, reason: str = None):
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.FAILED]:
            logger.warning(f"Attempted to cancel already closed order {order.id}")
            return False

        order.status = OrderStatus.CANCELLED
        order.save()
        logger.info(f"Order {order.id} cancelled. Reason: {reason}")
        return True

    @staticmethod
    def get_order_by_id(order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order with ID {order_id} does not exist.")
            return None

    @staticmethod
    def handle_order_status(order: Order, status: str):
        """
        Handles the order status update and performs necessary actions based on the new status.

        Args:
            order (Order): The order instance to be updated.
            status (str): The new status to be set for the order.

        Raises:
            ValueError: If the provided status is not valid.
        """
        if status == OrderStatus.COMPLETED:
            OrderServices.mark_items_as_sold(order)
            logger.info(f"Order {order.id} marked as completed.")
        elif status in [OrderStatus.CANCELLED, OrderStatus.FAILED]:
            # If the order is cancelled or failed, we need to revert the items to unsold status
            OrderServices.cancel_order(order)
            logger.info(f"Order {order.id} marked as cancelled.")
        else:
            raise ValueError(f"Invalid order status: {status}")

    @staticmethod
    def delete_expired_orders():
        """
        Deletes all orders that are in the CANCELLED status.
        """
        cancelled_orders = Order.objects.filter(status=OrderStatus.CANCELLED)
        cancelled_orders.delete()
        logger.info(f"Deleted {cancelled_orders.count()} cancelled orders.")
