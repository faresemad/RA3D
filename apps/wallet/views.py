import logging

from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.services.wallet import WalletService
from apps.utils.permissions import IsSupport
from apps.wallet.models import Wallet, WithdrawalRequest
from apps.wallet.serializers import (
    WalletSerializer,
    WithdrawalRequestActionSerializer,
    WithdrawalRequestListSerializer,
    WithdrawalRequestSerializer,
)

logger = logging.getLogger(__name__)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def balance(self, request: HttpRequest):
        wallet = WalletService.get_wallet(request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="transaction-history")
    def transaction_history(self, request: HttpRequest):
        wallet = WalletService.get_wallet(request.user)
        transactions = WalletService.get_transaction_history(wallet)

        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="transaction-count")
    def transaction_count(self, request: HttpRequest):
        wallet = WalletService.get_wallet(request.user)
        count = WalletService.get_transaction_count(wallet)
        return Response({"transaction_count": count})


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    queryset = WithdrawalRequest.objects.select_related("user").order_by("-created_at")
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["status", "payment_method"]
    ordering_fields = ["created_at", "amount"]
    search_fields = ["user__username", "transaction_id"]
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action in ["approve", "reject", "complete"]:
            self.permission_classes = [IsSupport | IsAdminUser]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in "list":
            return WithdrawalRequestListSerializer
        elif self.action in ["approve", "reject", "complete"]:
            return WithdrawalRequestActionSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_staff:
            logger.info(f"Staff user {self.request.user.username} accessed all withdrawal requests")
            return WithdrawalRequest.objects.all()
        logger.info(f"User {self.request.user.username} accessed their withdrawal requests")
        return WithdrawalRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        logger.info(f"User {self.request.user.username} created a new withdrawal request")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        if request.user.is_staff:
            withdrawal.approve()
            logger.info(f"Staff user {request.user.username} approved withdrawal request {pk}")
            return Response({"status": "withdrawal request approved"})
        logger.warning(f"User {request.user.username} attempted to approve withdrawal request {pk} without permission")
        return Response(
            {"error": "You do not have permission to approve withdrawal requests"}, status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=["get"])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        if request.user.is_staff:
            withdrawal.reject()
            logger.info(f"Staff user {request.user.username} rejected withdrawal request {pk}")
            return Response({"status": "withdrawal request rejected"})
        logger.warning(f"User {request.user.username} attempted to reject withdrawal request {pk} without permission")
        return Response(
            {"error": "You do not have permission to reject withdrawal requests"}, status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        withdrawal = self.get_object()
        serializer = WithdrawalRequestActionSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid data for completing withdrawal request {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.refresh_from_db()
        transaction_id = serializer.validated_data["transaction_id"]
        withdrawal._complete(transaction_id)
        logger.info(f"Withdrawal request {pk} completed with transaction ID: {transaction_id}")
        return Response({"status": "withdrawal request completed"})
