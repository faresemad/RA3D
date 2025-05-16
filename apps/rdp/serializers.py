import logging

from django.db.models.signals import post_save
from rest_framework import serializers

from apps.rdp.models import Rdp
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class RdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rdp
        fields = [
            "id",
            "ip",
            "hosting",
            "location",
            "username",
            "password",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "status",
            "windows_type",
            "access_type",
            "details",
            "created_at",
            "is_deleted",
        ]


class RdpListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    ip = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Rdp
        fields = [
            "id",
            "hosting",
            "location",
            "user",
            "ip",
            "username",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "status",
            "windows_type",
            "access_type",
            "created_at",
        ]

    def get_ip(self, obj: Rdp):
        ip_parts = obj.ip.split(".")
        return f"{ip_parts[0]}.{ip_parts[1]}.*.*"

    def get_username(self, obj: Rdp):
        return f"{obj.username[:2]}***"


class BulkCreateRdpSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of rdps."""

    def create(self, validated_data):
        # Create multiple Rdp objects at once
        rdps = [Rdp(**data) for data in validated_data]
        rdp_instances = Rdp.objects.bulk_create(rdps)

        logger.debug("Triggering post_save signals")
        for instance in rdp_instances:
            post_save.send(sender=Rdp, instance=instance, created=True)

        logger.info(f"Successfully created {len(rdp_instances)} RDPs")
        return rdp_instances


class CreateRdpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rdp
        fields = [
            "user",
            "ip",
            "username",
            "password",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "windows_type",
            "access_type",
        ]
        list_serializer_class = BulkCreateRdpSerializer
