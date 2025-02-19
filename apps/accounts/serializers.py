import logging
import re
from decimal import Decimal

from rest_framework import serializers

from apps.accounts.models import Account, AccountCategory, AccountStatus, AccountType
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


class BulkCreateAccountTextSerializer(serializers.Serializer):
    data = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Parse textarea input and validate each account entry.
        Expected format:
        domain | username | password | category | country | type | details | notes | price | proof
        """
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        accounts = []
        errors = []

        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) != 10:
                errors.append(f"Line {index}: Incorrect number of columns (Expected 10, got {len(parts)})")
                continue

            domain, username, password, category, country, type_, details, notes, price, proof = (
                p.strip() for p in parts
            )

            # Validate numeric fields
            try:
                price = Decimal(price)
                if price < 1:
                    errors.append(f"Line {index}: Price must be at least 1")
            except Exception:
                errors.append(f"Line {index}: Invalid price format")

            # Validate category and type choices
            if category not in dict(AccountCategory.choices):
                errors.append(f"Line {index}: Invalid category '{category}'")
            if type_ not in dict(AccountType.choices):
                errors.append(f"Line {index}: Invalid type '{type_}'")

            # Validate proof URL
            if not re.match(r"^https?:\/\/((?:vgy\.me|prnt\.sc|gyazo\.com)\/.*)", proof):
                errors.append(f"Line {index}: Invalid proof URL")

            # Add valid accounts
            if not errors:
                accounts.append(
                    {
                        "domain": domain,
                        "username": username,
                        "password": password,
                        "category": category,
                        "country": country,
                        "type": type_,
                        "details": details,
                        "notes": notes,
                        "price": price,
                        "proof": proof,
                        "status": AccountStatus.UNSOLD,
                        "is_sold": False,
                    }
                )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        return {"accounts": accounts}  # Ensure 'accounts' key exists

    def create(self, validated_data):
        """Bulk create accounts"""
        request_user = self.context["request"].user  # Get the user from the request
        accounts_data = validated_data["accounts"]

        # Assign user to all accounts
        for account_data in accounts_data:
            account_data["user"] = request_user

        accounts = [Account(**data) for data in accounts_data]
        return Account.objects.bulk_create(accounts)
