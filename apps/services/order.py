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
from apps.utils.notification import send_notification
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
        items_to_mark = [order.account, order.cpanel, order.rdp, order.shell, order.smtp, order.webmail]

        for item in items_to_mark:
            if item:
                item.mark_as_sold()
        send_notification(user=order.user, message=f"Order is Payed Successfully, ID: {str(order.id)}")
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
        elif status == OrderStatus.PENDING:
            # If the order is pending, we can do nothing or log it
            logger.info(f"Order {order.id} is still pending.")
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


class ReservationService:
    """
    A service class for managing product reservations in an order system.

    This class handles the reservation of products for an order, including:
    - Reserving products for a specific duration
    - Checking reservation validity
    - Releasing expired reservations
    - Releasing individual order products

    Attributes:
        RESERVATION_DURATION (timedelta): The default duration for product reservations (15 minutes).
    """

    RESERVATION_DURATION = timedelta(minutes=15)

    @classmethod
    def reserve_products(cls, order: Order) -> None:
        """
        Reserves products for a given order within a single transaction.

        This method attempts to reserve all products associated with an order by:
        - Checking product availability
        - Marking the order as reserved
        - Setting reservation expiration time
        - Updating product availability status

        Args:
            order (Order): The order for which products are to be reserved.

        Raises:
            ValueError: If any product in the order is not available.

        Side effects:
            - Updates order reservation status
            - Marks associated products as unavailable
            - Logs reservation details
        """
        with transaction.atomic():
            products = []
            for field in ["account", "cpanel", "rdp", "shell", "smtp", "webmail"]:
                if product := getattr(order, field):
                    product = product.__class__.objects.select_for_update().get(pk=product.pk)
                    if not product.is_available:
                        logger.error(f"Product {field} is not available for order {order.id}")
                        raise ValueError(f"Product {field} is not available")
                    products.append(product)

            now = timezone.now()
            order.is_reserved = True
            order.reserved_at = now
            order.reservation_expires = now + cls.RESERVATION_DURATION
            order.save()
            logger.info(f"Order {order.id} reserved successfully until {order.reservation_expires}")

            for product in products:
                product.is_available = False
                product.save()
                logger.info(f"Product {product.id} marked as reserved for order {order.id}")

    @classmethod
    def check_reservation(cls, order: Order) -> bool:
        """
        Checks the reservation status of an order.

        Verifies if an order is currently reserved and not expired.

        Args:
            order (Order): The order to check for active reservation.

        Returns:
            bool: True if the order is reserved and the reservation is still valid, False otherwise.

        Logs:
            - Debug message indicating reservation status
            - Debug message with specific reservation validity
        """
        if not order.is_reserved:
            logger.debug(f"Order {order.id} is not reserved")
            return False
        is_valid = timezone.now() < order.reservation_expires
        logger.debug(f"Order {order.id} reservation status: {'valid' if is_valid else 'expired'}")
        return is_valid

    @classmethod
    def release_expired_reservations(cls):
        """
        Releases reservations for orders that have exceeded their reservation time.

        Finds and processes all orders with expired reservations:
        - Identifies orders where reservation has passed current time
        - Releases associated products back to available status
        - Resets order's reserved status
        - Logs details of expired reservations processed

        Performs operations within a database transaction to ensure data consistency.
        """
        expired_orders = Order.objects.filter(is_reserved=True, reservation_expires__lt=timezone.now())
        logger.info(f"Found {expired_orders.count()} expired reservations")

        for order in expired_orders:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(pk=order.pk)
                if order.is_reserved and order.reservation_expires < timezone.now():
                    cls._release_order_products(order)
                    order.is_reserved = False
                    order.save()
                    logger.info(f"Released expired reservation for order {order.id}")

    @classmethod
    def _release_order_products(cls, order: Order) -> None:
        """
        Releases products associated with a given order back to available status.

        Iterates through specific product types (account, cpanel, rdp, shell, smtp, webmail)
        and updates their availability if they are associated with the order.

        Args:
            order (Order): The order whose products are to be released.

        Side effects:
            - Updates product availability status in the database
            - Logs information about each released product
        """
        for field in ["account", "cpanel", "rdp", "shell", "smtp", "webmail"]:
            if product := getattr(order, field):
                product.__class__.objects.filter(pk=product.pk).update(is_available=True)
                logger.info(f"Released product {product.id} from order {order.id}")
