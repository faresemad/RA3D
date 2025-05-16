import logging

from rest_framework import serializers

from apps.accounts.models import Account
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class BuyerAccountSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "category",
            "country",
            "type",
            "details",
            "price",
            "proof",
            "status",
            "is_sold",
            "created_at",
        ]


class OwnerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
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
        ]


class BulkCreateAccountSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of accounts."""

    def create(self, validated_data):
        # Create multiple Account objects at once
        accounts = [Account(**data) for data in validated_data]
        return Account.objects.bulk_create(accounts)


class CreateAccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Account
        exclude = ["status", "is_sold"]
        list_serializer_class = BulkCreateAccountSerializer
