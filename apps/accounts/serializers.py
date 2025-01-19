from rest_framework import serializers

from apps.accounts.models import Account
from apps.users.api.serializers.profile import UserProfileSerializer


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
    user = UserProfileSerializer()

    class Meta:
        model = Account
        fields = [
            "id",
            "user",
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


class CreateAccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Account
        exclude = ["status", "is_sold"]
