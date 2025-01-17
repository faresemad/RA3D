from rest_framework import serializers

from apps.smtp.models import SMTP
from apps.users.api.serializers.profile import UserProfileSerializer


class SmtpSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = SMTP
        fields = [
            "id",
            "user",
            "ip",
            "port",
            "smtp_type",
            "status",
            "price",
            "created_at",
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
