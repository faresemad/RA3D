import re

from rest_framework import serializers

from apps.cpanel.models import CPanel
from apps.users.api.serializers.profile import UserProfileSerializer


class CPanelSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    host = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = CPanel
        fields = [
            "id",
            "user",
            "host",
            "username",
            "price",
            "ssl",
            "tld",
            "cpanel_type",
            "status",
            "details",
            "created_at",
        ]

    def get_host(self, obj: CPanel):
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", obj.host):
            # It's an IP address
            return f"{obj.host.split('.')[0]}.{obj.host.split('.')[1]}.*.*"
        else:
            # It's a domain
            host_parts = obj.host.split(".")
            return f"{host_parts[0]}.{host_parts[1]}.*.*"

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
