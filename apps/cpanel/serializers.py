import logging
from decimal import Decimal

from django.db.models.signals import post_save
from rest_framework import serializers

from apps.cpanel.models import CPanel, CPanelStatus, CPanelType
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class UserCPanelSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = CPanel
        fields = [
            "id",
            "user",
            "username",
            "price",
            "ssl",
            "tld",
            "cpanel_type",
            "status",
            "hosting",
            "location",
            "created_at",
        ]

    def get_username(self, obj: CPanel):
        return f"{obj.username[:2]}***"


class OwnerCPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPanel
        fields = [
            "id",
            "host",
            "username",
            "password",
            "price",
            "cpanel_type",
            "status",
            "ssl",
            "tld",
            "details",
            "hosting",
            "location",
            "created_at",
        ]


class CreateCPanelSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CPanel
        fields = [
            "user",
            "host",
            "username",
            "password",
            "price",
            "cpanel_type",
        ]


class BulkCreateCPanelTextSerializer(serializers.Serializer):
    data = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Parse textarea input and validate each CPanel entry.
        Expected format:
        host | username | password | price | cpanel_type
        """
        logger.info("Starting validation of bulk CPanel data")
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        cpanels = []
        errors = []

        logger.debug(f"Processing {len(lines)} lines of CPanel data")
        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) != 5:
                logger.warning(f"Line {index} has incorrect number of columns: {len(parts)}")
                errors.append(f"Line {index}: Incorrect number of columns (Expected 5, got {len(parts)})")
                continue

            host, username, password, price, cpanel_type = (p.strip() for p in parts)

            try:
                price = Decimal(price)
                if price < 1:
                    logger.warning(f"Line {index} has invalid price: {price}")
                    errors.append(f"Line {index}: Price must be at least 1")
            except ValueError:
                logger.warning(f"Line {index} has invalid price format: {price}")
                errors.append(f"Line {index}: Invalid price format")

            if cpanel_type not in dict(CPanelType.choices):
                logger.warning(f"Line {index} has invalid cPanel type: {cpanel_type}")
                errors.append(f"Line {index}: Invalid cPanel type '{cpanel_type}'")

            if not errors:
                logger.debug(f"Line {index} validated successfully")
                cpanels.append(
                    {
                        "host": host,
                        "username": username,
                        "password": password,
                        "price": price,
                        "cpanel_type": cpanel_type,
                        "status": CPanelStatus.UNSOLD,
                        "ssl": False,
                        "tld": None,
                        "hosting": None,
                        "location": None,
                        "details": {},
                    }
                )

        if errors:
            logger.error(f"Validation failed with {len(errors)} errors")
            raise serializers.ValidationError({"errors": errors})

        logger.info(f"Validation completed successfully. {len(cpanels)} CPanels ready for creation")
        return {"cpanels": cpanels}

    def create(self, validated_data):
        """Bulk create cPanel records and manually trigger post_save signal"""
        logger.info("Starting bulk creation of CPanels")
        request_user = self.context["request"].user
        cpanels_data = validated_data["cpanels"]

        for cpanel_data in cpanels_data:
            cpanel_data["user"] = request_user

        logger.debug(f"Creating {len(cpanels_data)} CPanel instances")
        cpanel_instances = CPanel.objects.bulk_create([CPanel(**data) for data in cpanels_data])

        logger.debug("Triggering post_save signals")
        for instance in cpanel_instances:
            post_save.send(sender=CPanel, instance=instance, created=True)

        logger.info(f"Successfully created {len(cpanel_instances)} CPanels")
        return cpanel_instances
