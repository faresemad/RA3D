from rest_framework import viewsets

from apps.accounts.models import Account, AccountCategory, AccountData
from apps.accounts.serializers import (
    AccountCategorySerializer,
    AccountDataSerializer,
    AccountSerializer,
    CreateAccountDataSerializer,
)


class AccountDataViewSet(viewsets.ModelViewSet):
    queryset = AccountData.objects.all()
    serializer_class = AccountDataSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateAccountDataSerializer
        return AccountDataSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountCategoryViewSet(viewsets.ModelViewSet):
    queryset = AccountCategory.objects.all()
    serializer_class = AccountCategorySerializer
