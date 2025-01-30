import logging

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, Transaction
from apps.orders.serializers import OrderSerializer, TransactionSerializer
from apps.services.coingate import CoinGateService
from apps.services.transaction import TransactionService

logger = logging.getLogger(__name__)

coingate_service = CoinGateService()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get cryptocurrency from request data
        cryptocurrency = request.data.get("cryptocurrency")

        if not cryptocurrency:
            return Response({"error": "Cryptocurrency selection is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Add cryptocurrency to serializer context
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context["cryptocurrency"] = cryptocurrency

        try:
            self.perform_create(serializer)
            order = serializer.instance
            return Response(
                {"order_id": str(order.id), "payment_url": Transaction.objects.get(order=order).payment_url},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CoinGateWebhookView(APIView):
    def post(self, request):
        if not coingate_service.verify_webhook_signature(request.headers, request.body):
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.data
        transaction_id = data.get("id")
        cg_status = data.get("status")

        try:
            mapped_status = coingate_service.map_payment_status(cg_status)
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
