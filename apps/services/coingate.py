# services/coingate.py
import hashlib
import hmac
import logging

import requests
from django.conf import settings

from apps.orders.models import Transaction

logger = logging.getLogger(__name__)


class CoinGateService:
    def __init__(self):
        self.api_key = settings.COINGATE_API_KEY
        self.sandbox = settings.COINGATE_SANDBOX
        self.base_url = settings.BASE_URL
        self.backend_url = settings.BACKEND_URL
        self.api_url = (
            "https://api-sandbox.coingate.com/v2/orders" if self.sandbox else "https://api.coingate.com/v2/orders"
        )
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def create_order(self, order, cryptocurrency):
        """
        Create a new CoinGate order for payment processing
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

            response = requests.post(self.api_url, headers=self.headers, data=data)
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
        Verify the authenticity of CoinGate webhook requests
        """
        try:
            received_signature = headers.get("X-Request-Signature", "")
            generated_signature = hmac.new(settings.COINGATE_API_KEY.encode(), body, hashlib.sha256).hexdigest()

            return hmac.compare_digest(received_signature, generated_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    @staticmethod
    def map_payment_status(coingate_status):
        """
        Map CoinGate payment statuses to our internal status system
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
