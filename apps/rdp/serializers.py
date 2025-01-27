from rest_framework import serializers

from apps.rdp.models import Rdp
from apps.users.api.serializers.profile import UserProfileSerializer


class RdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rdp
        fields = [
            "id",
            "ip",
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
            "details",
            "created_at",
        ]

    def get_ip(self, obj: Rdp):
        ip_parts = obj.ip.split(".")
        return f"{ip_parts[0]}.{ip_parts[1]}.*.*"

    def get_username(self, obj: Rdp):
        return f"{obj.username[:2]}***"


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
