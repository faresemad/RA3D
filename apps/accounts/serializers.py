from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import Account, AccountCategory, AccountData


class AccountCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountCategory
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class CreateAccountDataSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = AccountData
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        account_obj = validated_data.pop("account")
        account = Account.objects.create(**account_obj)
        account_data = AccountData.objects.create(account=account, **validated_data)
        return account_data


class AccountDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountData
        fields = "__all__"
