import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.filters import AccountFilter
from apps.accounts.models import Account
from apps.accounts.serializers import BuyerAccountSerializer, CreateAccountSerializer, OwnerAccountSerializer
from apps.utils.permissions import IsAccountAdmin, IsOwner, IsSeller

logger = logging.getLogger(__name__)


class SellerAccountViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = OwnerAccountSerializer
    permission_classes = [IsOwner, IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AccountFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "details", "user__username"]

    def get_queryset(self):
        queryset = Account.objects.filter(user=self.request.user).only(
            "domain",
            "username",
            "password",
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
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [(IsAccountAdmin | IsSeller)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateAccountSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """Support bulk creation of accounts."""
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
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

    @action(detail=True, methods=["post"])
    def mark_as_sold(self, request, pk=None):
        account = self.get_object()
        account.mark_as_sold()
        logger.info(f"Account {pk} marked as sold by {request.user.username}")
        return Response({"status": "success", "message": "Account marked as sold"})

    @action(detail=True, methods=["post"])
    def mark_as_unsold(self, request, pk=None):
        account = self.get_object()
        account.mark_as_unsold()
        logger.info(f"Account {pk} marked as unsold by {request.user.username}")
        return Response({"status": "success", "message": "Account marked as unsold"})

    @action(detail=True, methods=["post"])
    def mark_as_deleted(self, request, pk=None):
        account = self.get_object()
        account.mark_as_deleted()
        logger.info(f"Account {pk} marked as deleted by {request.user.username}")
        return Response({"status": "success", "message": "Account marked as deleted"})


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
    serializer_class = BuyerAccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AccountFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "details", "user__username"]


class CountryOfAccounts(viewsets.ViewSet):
    """
    View to list all countries of accounts.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Account.objects.values_list("country", flat=True).distinct().order_by("country")
        return list(set(queryset))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset, status=status.HTTP_200_OK)
