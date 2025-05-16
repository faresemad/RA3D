import logging

from django.db.models.signals import post_save
from rest_framework import serializers

from apps.cpanel.models import CPanel
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


class BulkCreateCPanelSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of cpanels."""

    def create(self, validated_data):
        # Create multiple CPanel objects at once
        cpanels = [CPanel(**data) for data in validated_data]
        cpanel_instances = CPanel.objects.bulk_create(cpanels)
        logger.debug("Triggering post_save signals")
        for instance in cpanel_instances:
            post_save.send(sender=CPanel, instance=instance, created=True)

        logger.info(f"Successfully created {len(cpanel_instances)} CPanels")
        return cpanel_instances


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
        list_serializer_class = BulkCreateCPanelSerializer
