import logging

import requests
from django.conf import settings

from apps.orders.models import Order, Transaction

logger = logging.getLogger(__name__)


class CoinGateService:
    """
    A service class for handling CoinGate cryptocurrency payment integrations.

    This class provides methods for creating payment orders, verifying webhook signatures,
    generating request signatures, and mapping payment statuses between CoinGate and the
    application's internal transaction status system.

    Attributes:
        api_key (str): CoinGate API key for authentication
        sandbox (bool): Flag to determine whether to use sandbox or production environment
        base_url (str): Base URL for frontend redirects
        backend_url (str): Backend URL for webhook callbacks
        api_url (str): CoinGate API endpoint URL
    """

    def __init__(self):
        self.api_key = settings.COINGATE_API_KEY
        self.sandbox = settings.COINGATE_SANDBOX
        self.base_url = settings.BASE_URL
        self.backend_url = settings.BACKEND_URL
        self.api_url = (
            "https://api-sandbox.coingate.com/v2/orders" if self.sandbox else "https://api.coingate.com/v2/orders"
        )

    def create_order(self, order: Order, cryptocurrency):
        """
        Create a new payment order with CoinGate for cryptocurrency transactions.

        This method generates a CoinGate order by preparing transaction details,
        creating a signature, and sending a request to the CoinGate API.

        Args:
            order (Order): The order object containing transaction details
            cryptocurrency (str): The cryptocurrency to be used for payment

        Returns:
            dict or None: CoinGate order response if successful, None otherwise

        Raises:
            requests.RequestException: If there's an error communicating with the CoinGate API
        """
        try:
            data = {
                "order_id": str(order.id),
                "price_amount": float(order.total_price),
                "price_currency": "USD",
                "receive_currency": cryptocurrency,
                "callback_url": f"{self.backend_url}/api/orders/webhook/coingate/",
                "cancel_url": f"{self.base_url}/payment/cancel/",
                "success_url": f"{self.base_url}/payment/success/",
                "title": f"Order #{order.id}",
                "description": f"Payment for Order #{order.id}",
            }

            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

            response = requests.post(self.api_url, headers=headers, data=data)
            response.raise_for_status()

            logger.info(f"Created CoinGate order for Order {order.id}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"CoinGate API Error: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"CoinGate API Error Details: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating CoinGate order: {str(e)}")
            return None

    @staticmethod
    def map_payment_status(coingate_status):
        """
        Map a CoinGate payment status to the corresponding internal payment status.

        This method translates CoinGate-specific payment statuses into the application's
        standardized payment status enum, providing a consistent status representation
        across different payment providers.

        Args:
            coingate_status (str): The original payment status from CoinGate

        Returns:
            Transaction.PaymentStatus: The mapped internal payment status, defaulting to FAILED
            if no matching status is found
        """
        status_mapping = {
            "paid": Transaction.PaymentStatus.COMPLETED,
            "pending": Transaction.PaymentStatus.PENDING,
            "confirmed": Transaction.PaymentStatus.COMPLETED,
            "invalid": Transaction.PaymentStatus.FAILED,
            "expired": Transaction.PaymentStatus.FAILED,
            "canceled": Transaction.PaymentStatus.FAILED,
        }
        return status_mapping.get(coingate_status, Transaction.PaymentStatus.FAILED)
