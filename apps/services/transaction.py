# services/transactions.py
import logging

from django.utils import timezone

from apps.orders.models import OrderStatus, Transaction

logger = logging.getLogger(__name__)


class TransactionService:
    @staticmethod
    def create_transaction(order, coingate_order, cryptocurrency):
        """
        Create a new transaction record from CoinGate response
        """
        try:
            if cryptocurrency not in Transaction.Cryptocurrency.values:
                raise ValueError(f"Invalid cryptocurrency: {cryptocurrency}")
            transaction = Transaction.objects.create(
                order=order,
                transaction_id=coingate_order["id"],
                payment_url=coingate_order["payment_url"],
                cryptocurrency=cryptocurrency,
                amount=coingate_order["receive_amount"],
                payment_status=Transaction.PaymentStatus.PENDING,
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
            return TransactionService.handle_order_status_update(transaction)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found")
            raise
        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {str(e)}")
            raise

    @staticmethod
    def handle_order_status_update(transaction):
        """
        Update related order status based on transaction status
        """
        order = transaction.order
        if transaction.payment_status == Transaction.PaymentStatus.COMPLETED:
            order.status = OrderStatus.COMPLETED
        elif transaction.payment_status == Transaction.PaymentStatus.FAILED:
            order.status = OrderStatus.FAILED

        order.save()
        logger.info(f"Updated order {order.id} to status {order.status}")
        return order

    @staticmethod
    def get_user_transactions(user):
        """
        Retrieve all transactions for a specific user
        """
        return Transaction.objects.filter(order__user=user).select_related("order")
