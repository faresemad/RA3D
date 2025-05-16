import logging

from django.db.models.signals import post_save
from rest_framework import serializers

from apps.smtp.models import SMTP
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class SmtpListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    ip = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = SMTP
        fields = [
            "id",
            "user",
            "ip",
            "username",
            "hosting",
            "location",
            "port",
            "smtp_type",
            "status",
            "price",
            "created_at",
        ]

    def get_ip(self, obj: SMTP):
        ip_parts = obj.ip.split(".")
        return f"{ip_parts[0]}.{ip_parts[1]}.*.*"

    def get_username(self, obj: SMTP):
        return f"{obj.username[:2]}***"


class SmtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTP
        fields = [
            "id",
            "ip",
            "port",
            "username",
            "password",
            "hosting",
            "location",
            "smtp_type",
            "status",
            "price",
            "created_at",
            "is_deleted",
        ]


class BulkCreateSMTPSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of smtps."""

    def create(self, validated_data):
        # Create multiple SMTPs objects at once
        smtps = [SMTP(**data) for data in validated_data]
        smtps_instances = SMTP.objects.bulk_create(smtps)

        logger.debug("Triggering post_save signals")
        for instance in smtps_instances:
            post_save.send(sender=SMTP, instance=instance, created=True)

        logger.info(f"Successfully created {len(smtps_instances)} SMTPs")
        return smtps_instances


class CreateSmtpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SMTP
        fields = [
            "id",
            "user",
            "ip",
            "port",
            "username",
            "password",
            "smtp_type",
            "price",
        ]
        list_serializer_class = BulkCreateSMTPSerializer
