import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.filters import AccountFilter
from apps.accounts.models import Account, AccountCategory, AccountData
from apps.accounts.serializers import AccountSerializer, CategorySerializer, CreateAccountDataSerializer

logger = logging.getLogger(__name__)


class AccountDataViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AccountData.objects.all()
    serializer_class = CreateAccountDataSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Account data created successfully.")
        return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)


class AccountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Account.objects.select_related("user", "category")
        .filter(is_sold=False)
        .only(
            "user__username",
            "user__picture",
            "category__name",
            "website_domain",
            "location",
            "details",
            "price",
            "source",
            "proof",
            "created_at",
            "is_sold",
        )
    )
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AccountFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user", "location", "source", "is_sold", "created_at", "website_domain"]


class AccountCategoryViewSet(viewsets.ModelViewSet):
    queryset = AccountCategory.objects.all().order_by("-created_at")
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Account category created successfully.")
        return Response({"message": "Account category created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        logger.info("Account category updated successfully.")
        return Response({"message": "Account category updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        logger.info("Account category deleted successfully.")
        return Response({"message": "Account category deleted successfully."}, status=status.HTTP_200_OK)
