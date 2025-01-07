import logging

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Account, AccountCategory, AccountData
from apps.accounts.serializers import (
    AccountCategorySerializer,
    AccountDataSerializer,
    AccountSerializer,
    CreateAccountDataSerializer,
)

logger = logging.getLogger(__name__)


class AccountDataViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AccountData.objects.all()
    serializer_class = AccountDataSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateAccountDataSerializer
        return AccountDataSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Account data created successfully.")
        return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)


class AccountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]


class AccountCategoryViewSet(viewsets.ModelViewSet):
    queryset = AccountCategory.objects.all()
    serializer_class = AccountCategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
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
