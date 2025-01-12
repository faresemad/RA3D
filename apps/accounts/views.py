import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.filters import AccountFilter
from apps.accounts.models import Account
from apps.accounts.serializers import AccountSerializer, CreateAccountSerializer
from apps.utils.permissions import IsSeller

logger = logging.getLogger(__name__)


class AccountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Account.objects.select_related("user")
        .filter(is_sold=False)
        .only(
            "user__username",
            "user__picture",
            "category",
            "country",
            "type",
            "details",
            "price",
            "proof",
            "status",
            "is_sold",
            "created_at",
        )
    )
    serializer_class = AccountSerializer
    permission_classes = [IsSeller]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AccountFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "details", "user__username"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateAccountSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"Account created by {request.user.username}")
        return Response(
            {
                "status": "success",
                "message": "Account created successfully",
            },
            status=status.HTTP_201_CREATED,
        )
