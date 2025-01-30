from django.http import HttpRequest
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.services.wallet import WalletService
from apps.wallet.models import Wallet
from apps.wallet.serializers import WalletSerializer


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
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="transaction-count")
    def transaction_count(self, request: HttpRequest):
        wallet = WalletService.get_wallet(request.user)
        count = WalletService.get_transaction_count(wallet)
        return Response({"transaction_count": count})
