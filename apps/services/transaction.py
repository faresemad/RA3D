# services/transactions.py
import logging

from django.utils import timezone

from apps.orders.models import OrderStatus, Transaction

logger = logging.getLogger(__name__)


class TransactionService:
    @staticmethod
    def create_transaction(order, coingate_order, cryptocurrency):
        logger.info(f"Creating coingate_order {coingate_order} for order {order.id}")
        """
        Create a new transaction record from CoinGate response
        {
            'id': 201386,
            'status': 'new',
            'title': None,
            'do_not_convert': False,
            'orderable_type': 'ApiApp',
            'orderable_id': 2876,
            'uuid': 'ee25fd6f-bf34-426a-a464-d38c6540e7c0',
            'payment_gateway': None,
            'price_currency': 'USD',
            'price_amount': '10.0',
            'lightning_network': False,
            'receive_currency': 'BTC',
            'receive_amount': '0',
            'created_at': '2025-01-30T21:48:54+00:00',
            'order_id': 'c12e22ea-5cb3-47db-806e-0d9ff711b138',
            'payment_url': 'https://pay-sandbox.coingate.com/invoice/ee25fd6f-bf34-426a-a464-d38c6540e7c0',
            'underpaid_amount': '0',
            'overpaid_amount': '0',
            'is_refundable': False,
            'payment_request_uri': None,
            'refunds': [],
            'voids': [],
            'fees': [],
            'blockchain_transactions': [],
            'token': 'h_2K_MznfEx2fxmUyLyprJJwsxsdsQ'
        }
        """
        try:
            if cryptocurrency not in Transaction.Cryptocurrency.values:
                raise ValueError(f"Invalid cryptocurrency: {cryptocurrency}")
            transaction = Transaction.objects.create(
                order=order,
                transaction_id=coingate_order["id"],
                payment_url=coingate_order["payment_url"],
                cryptocurrency=cryptocurrency,
                amount=coingate_order["price_amount"],
                payment_status=Transaction.PaymentStatus.PENDING,
                payment_date=coingate_order["created_at"],
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
