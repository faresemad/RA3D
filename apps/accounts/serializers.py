from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import Account, AccountCategory, AccountData
from apps.users.api.serializers.profile import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountCategory
        fields = "__all__"


class AccountCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountCategory
        fields = ["id", "name"]


class AccountSerializer(serializers.ModelSerializer):
    category = AccountCategorySerializer()
    user = UserProfileSerializer()

    class Meta:
        model = Account
        exclude = ["is_sold", "updated_at"]


class CreateAccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=AccountCategory.objects.only("id", "name"))

    class Meta:
        model = Account
        fields = "__all__"


class CreateAccountDataSerializer(serializers.ModelSerializer):
    account = CreateAccountSerializer()

    class Meta:
        model = AccountData
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        account_obj = validated_data.pop("account")
        account = Account.objects.create(**account_obj)
        account_data = AccountData.objects.create(account=account, **validated_data)
        return account_data
