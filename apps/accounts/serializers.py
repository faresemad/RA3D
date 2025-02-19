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
        logger.info("Starting bulk account validation")
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        accounts = []
        errors = []

        for index, line in enumerate(lines, start=1):
            logger.debug(f"Processing line {index}")
            parts = line.split("|")
            if len(parts) != 10:
                errors.append(f"Line {index}: Incorrect number of columns (Expected 10, got {len(parts)})")
                continue

            domain, username, password, category, country, type_, details, notes, price, proof = (
                p.strip() for p in parts
            )

            logger.debug(f"Validating numeric fields for line {index}")
            try:
                price = Decimal(price)
                if price < 1:
                    errors.append(f"Line {index}: Price must be at least 1")
            except Exception:
                errors.append(f"Line {index}: Invalid price format")

            logger.debug(f"Validating category and type choices for line {index}")
            if category not in dict(AccountCategory.choices):
                errors.append(f"Line {index}: Invalid category '{category}'")
            if type_ not in dict(AccountType.choices):
                errors.append(f"Line {index}: Invalid type '{type_}'")

            logger.debug(f"Validating proof URL for line {index}")
            if not re.match(r"^https?:\/\/((?:vgy\.me|prnt\.sc|gyazo\.com)\/.*)", proof):
                errors.append(f"Line {index}: Invalid proof URL")

            if not errors:
                logger.debug(f"Adding valid account data for line {index}")
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
            logger.error(f"Validation failed with {len(errors)} errors")
            raise serializers.ValidationError({"errors": errors})

        logger.info(f"Validation completed successfully with {len(accounts)} valid accounts")
        return {"accounts": accounts}

    def create(self, validated_data):
        logger.info("Starting bulk account creation")
        request_user = self.context["request"].user
        accounts_data = validated_data["accounts"]

        logger.debug("Assigning user to accounts")
        for account_data in accounts_data:
            account_data["user"] = request_user

        logger.debug("Creating account objects")
        accounts = [Account(**data) for data in accounts_data]
        created_accounts = Account.objects.bulk_create(accounts)
        logger.info(f"Successfully created {len(created_accounts)} accounts")
        return created_accounts
