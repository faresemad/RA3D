import logging

from django.utils import timezone

from apps.orders.models import OrderStatus, Transaction
from apps.services.order import OrderServices, ReservationService
from apps.services.wallet import WalletService
from apps.wallet.models import Wallet

logger = logging.getLogger(__name__)
wallet_service = WalletService()
order_service = OrderServices()


class TransactionService:
    @staticmethod
    def create_transaction(order, coingate_order, cryptocurrency):
        logger.info(f"Creating coingate_order {coingate_order} for order {order.id}")
        """
        Create a new transaction record from CoinGate response
        """
        try:
            if cryptocurrency not in Transaction.Cryptocurrency.values:
                raise ValueError(f"Invalid cryptocurrency: {cryptocurrency}")
            wallet = Wallet.objects.select_for_update().get(user=order.user)
            transaction = Transaction.objects.create(
                order=order,
                transaction_id=coingate_order["id"],
                payment_url=coingate_order["payment_url"],
                cryptocurrency=cryptocurrency,
                amount=coingate_order["price_amount"],
                payment_status=Transaction.PaymentStatus.PENDING,
                payment_date=coingate_order["created_at"],
                wallet=wallet,
            )
            logger.info(f"Created transaction {transaction.id} for order {order.id}")
            return transaction
        except Exception as e:
            logger.error(f"Failed to create transaction: {str(e)}")
            raise

    @staticmethod
    def create_plisio_transaction(order, plisio_order, cryptocurrency):
        logger.info(f"Creating plisio_order {plisio_order} for order {order.id}")
        """
        Create a new transaction record from Plisio response
        Args:
            order: Order instance
            plisio_order: Dictionary containing Plisio order data
            cryptocurrency: Selected cryptocurrency
        Returns:
            Transaction instance
        Raises:
            ValueError: If cryptocurrency is invalid
        """
        try:
            if cryptocurrency not in Transaction.Cryptocurrency.values:
                raise ValueError(f"Invalid cryptocurrency: {cryptocurrency}")

            order_data = plisio_order["data"]
            wallet = Wallet.objects.select_for_update().get(user=order.user)

            transaction = Transaction.objects.create(
                order=order,
                transaction_id=order_data["txn_id"],
                payment_url=order_data["invoice_url"],
                cryptocurrency=cryptocurrency,
                amount=order_data["invoice_total_sum"],
                payment_status=Transaction.PaymentStatus.PENDING,
                payment_date=timezone.now(),
                wallet=wallet,
            )

            logger.info(f"Created transaction {transaction.id} for order {order.id}")
            return transaction

        except Exception as e:
            logger.error(f"Failed to create transaction: {str(e)}")
            raise

    @staticmethod
    def update_transaction_status(transaction_id, new_status):
        """
        Update transaction status and related order status
        """
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.payment_status = new_status
            transaction.payment_date = timezone.now() if new_status == Transaction.PaymentStatus.COMPLETED else None
            transaction.save()

            logger.info(f"Updated transaction {transaction_id} to status {new_status}")
            TransactionService.handle_order_status_update(transaction)
            return True
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found")
            raise
        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {str(e)}")
            raise

    @staticmethod
    def handle_order_status_update(transaction: Transaction):
        """Updated to handle seller payout"""
        order = transaction.order

        if transaction.payment_status == Transaction.PaymentStatus.COMPLETED:
            order.status = OrderStatus.COMPLETED
            order.is_reserved = False
            order.save()
            # Credit seller wallet
            WalletService.handle_order_completion(order)
        elif transaction.payment_status == Transaction.PaymentStatus.FAILED:
            ReservationService._release_order_products(order)
            order.status = OrderStatus.FAILED
            order.is_reserved = False
            order.save()

        order_service.handle_order_status(order, order.status)
        logger.info(f"Updated order {order.id} to status {order.status}")
        return order

    @staticmethod
    def get_user_transactions(user):
        """
        Retrieve all transactions for a specific user
        """
        return Transaction.objects.filter(order__user=user).select_related("order")
