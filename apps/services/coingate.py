# services/coingate.py
import hashlib
import hmac
import logging

import requests
from django.conf import settings

from apps.orders.models import Transaction

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

    def create_order(self, order, cryptocurrency):
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
            }

            signature = self.generate_signature(data)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-Request-Signature": signature,
            }

            response = requests.post(self.api_url, headers=headers, data=data)
            response.raise_for_status()

            logger.info(f"Created CoinGate order for Order {order.id}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"CoinGate API Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating CoinGate order: {str(e)}")
            return None

    @staticmethod
    def verify_webhook_signature(headers, body):
        """
        Verify the signature of a CoinGate webhook request.

        This method compares the received signature from the webhook headers
        with a generated signature using the CoinGate API key.

        Args:
            headers (dict): HTTP headers containing the received signature
            body (bytes): Raw request body used to generate the signature

        Returns:
            bool: True if signatures match, False otherwise

        Raises:
            Exception: If signature verification encounters an error
        """
        try:
            received_signature = headers.get("X-Request-Signature", "")
            generated_signature = hmac.new(settings.COINGATE_API_KEY.encode(), body, hashlib.sha256).hexdigest()

            return hmac.compare_digest(received_signature, generated_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    @staticmethod
    def generate_signature(data):
        """
        Generate a signature for CoinGate API requests using HMAC-SHA256.

        This method creates a signature by concatenating all values from the input data
        and generating a hexadecimal digest using the CoinGate API key.

        Args:
            data (dict): A dictionary of request parameters to be signed

        Returns:
            str: A hexadecimal signature string, or None if signature generation fails

        Raises:
            Exception: Logs and returns None if signature generation encounters an error
        """
        try:
            message = "".join(str(value) for value in data.values())
            signature = hmac.new(settings.COINGATE_API_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Signature generation failed: {str(e)}")
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
