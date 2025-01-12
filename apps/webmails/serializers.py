from rest_framework import serializers

from apps.users.api.serializers.profile import UserProfileSerializer
from apps.webmails.models import WebMail


class WebMailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = WebMail
        exclude = ["updated_at", "username", "password"]


class CreateWebMailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = WebMail
        exclude = ["status", "is_sold"]
