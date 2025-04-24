import hashlib
import hmac
import logging

import requests
from django.conf import settings

from apps.orders.models import Order, Transaction

logger = logging.getLogger(__name__)


class PlisioService:
    def __init__(self):
        self.api_key = settings.PLIOSIO_API_KEY
        self.base_url = settings.BASE_URL
        self.api_url = "https://api.plisio.net/api/v1"

    def create_order(self, order: Order, cryptocurrency: str):
        """
        Create a new Plisio order for payment processing
        """
        try:
            params = {
                "order_number": str(order.id),
                "source_amount": float(order.total_price),
                "source_currency": "USD",
                "currency": str(cryptocurrency),
                "order_name": f"Order #{order.id}",
                "email": str(order.user.email),
                "description": f"Order #{order.id}",
                "callback_url": f"{self.base_url}/webhook/plisio/",
                "expire_min": 15,
                "api_key": str(self.api_key),
            }

            response = requests.get(f"{self.api_url}/invoices/new", params=params)
            response.raise_for_status()

            logger.info(f"Created Plisio order for Order {order.id}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Plisio API Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Plisio order: {str(e)}")
            return None

    @staticmethod
    def verify_webhook_signature(headers, body):
        """
        Verify the authenticity of Plisio webhook requests
        """
        try:
            received_signature = headers.get("X-Request-Signature", "")
            generated_signature = hmac.new(
                settings.PLIOSIO_API_KEY.encode(), body.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(received_signature, generated_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    @staticmethod
    def map_payment_status(plisio_status):
        """
        Map Plisio payment statuses to our internal status system
        """
        status_mapping = {
            "paid": Transaction.PaymentStatus.COMPLETED,
            "pending": Transaction.PaymentStatus.PENDING,
            "confirmed": Transaction.PaymentStatus.COMPLETED,
            "invalid": Transaction.PaymentStatus.FAILED,
            "expired": Transaction.PaymentStatus.FAILED,
            "canceled": Transaction.PaymentStatus.FAILED,
        }
        return status_mapping.get(plisio_status, Transaction.PaymentStatus.FAILED)
