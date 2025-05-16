import logging

from rest_framework import serializers

from apps.shells.models import Shell
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class ShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shell
        fields = [
            "id",
            "shell_url",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
            "is_deleted",
        ]


class ShellListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Shell
        fields = [
            "id",
            "user",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
        ]


class BulkCreateShellSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of shells."""

    def create(self, validated_data):
        # Create multiple Shell objects at once
        shells = [Shell(**data) for data in validated_data]
        return Shell.objects.bulk_create(shells)


class CreateShellSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shell
        fields = [
            "id",
            "user",
            "shell_url",
            "shell_type",
            "price",
        ]
        list_serializer_class = BulkCreateShellSerializer
