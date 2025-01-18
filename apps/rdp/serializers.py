from rest_framework import serializers

from apps.rdp.models import Rdp
from apps.users.api.serializers.profile import UserProfileSerializer


class RdpSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

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


class CreateRdpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rdp
        fields = [
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
        ]
