from rest_framework import serializers

from apps.smtp.models import SMTP
from apps.users.api.serializers.profile import UserProfileSerializer


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
            "smtp_type",
            "status",
            "price",
            "created_at",
            "is_deleted",
        ]


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
