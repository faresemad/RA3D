import logging

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers import CreateOrderSerializer, ListOrderSerializer

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("account", "cpanel", "rdp", "shell").only(
        "id",
        "account__domain",
        "cpanel__host",
        "rdp__ip",
        "shell__shell_url",
        "total_price",
        "status",
        "payment_method",
        "created_at",
    )
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ListOrderSerializer
        return CreateOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info(f"Order created: {serializer.data['id']}")
        return Response(
            {"id": serializer.data["id"], "success": True, "message": "Order created successfully."},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
