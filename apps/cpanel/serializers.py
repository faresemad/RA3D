from rest_framework import serializers

from apps.cpanel.models import CPanel
from apps.users.api.serializers.profile import UserProfileSerializer


class CPanelSerializer(serializers.ModelSerializer):
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
            "details",
            "created_at",
        ]

    def get_username(self, obj: CPanel):
        return f"{obj.username[:2]}***"


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
