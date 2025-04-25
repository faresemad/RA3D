import logging

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.helper.serializers import (
    SecretAccountSerializer,
    SecretCPanelSerializer,
    SecretRdpSerializer,
    SecretShellSerializer,
    SecretSMTPSerializer,
    SecretWebMailSerializer,
)
from apps.orders.models import Order, Transaction
from apps.orders.serializers import ListOrderSerializer, OrderSerializer, TransactionSerializer
from apps.services.coingate import CoinGateService
from apps.services.plisio import PlisioService
from apps.services.transaction import TransactionService

logger = logging.getLogger(__name__)

coingate_service = CoinGateService()
plisio_service = PlisioService()


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.select_related("user", "account", "cpanel", "rdp", "shell", "smtp", "webmail").filter(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ListOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
            order = serializer.instance
            transaction = Transaction.objects.select_related("order").get(order=order)
            return Response(
                {"order_id": str(order.id), "payment_url": transaction.payment_url},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="secret-data")
    def get_secret_data(self, request, pk=None):
        try:
            order = self.get_object()

            if order.account:
                serializer = SecretAccountSerializer(order.account)
            elif order.cpanel:
                serializer = SecretCPanelSerializer(order.cpanel)
            elif order.rdp:
                serializer = SecretRdpSerializer(order.rdp)
            elif order.shell:
                serializer = SecretShellSerializer(order.shell)
            elif order.smtp:
                serializer = SecretSMTPSerializer(order.smtp)
            elif order.webmail:
                serializer = SecretWebMailSerializer(order.webmail)
            else:
                return Response({"detail": "No secret data found."}, status=status.HTTP_204_NO_CONTENT)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving secret data: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CoinGateWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Received CoinGate webhook request")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Request body: {request.body}")

        if not coingate_service.verify_webhook_signature(request.headers, request.body):
            logger.warning("Invalid webhook signature")
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.data
        logger.info(f"CoinGate webhook data: {data}")
        transaction_id = data.get("id")
        cg_status = data.get("status")
        logger.info(f"Processing transaction ID: {transaction_id} with status: {cg_status}")

        try:
            mapped_status = coingate_service.map_payment_status(cg_status)
            logger.info(f"Mapped status: {mapped_status}")
            TransactionService.update_transaction_status(transaction_id, mapped_status)
            logger.info(f"Successfully updated transaction {transaction_id}")
            return Response(status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {transaction_id}")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlisioWebhookView(APIView):
    def post(self, request):
        if not plisio_service.verify_webhook_signature(request.headers, request.body):
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.data
        transaction_id = data.get("id")
        cg_status = data.get("status")

        try:
            mapped_status = plisio_service.map_payment_status(cg_status)
            TransactionService.update_transaction_status(transaction_id, mapped_status)
            return Response(status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TransactionService.get_user_transactions(self.request.user)


class PaymentSuccessView(APIView):
    def get(self, request):
        return Response({"status": "success", "message": "Payment completed successfully"})


class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {"status": "cancelled", "message": "Payment was cancelled"}, status=status.HTTP_400_BAD_REQUEST
        )
