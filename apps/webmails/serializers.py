import logging

from django.db.models.signals import post_save
from rest_framework import serializers

from apps.users.api.serializers.profile import UserProfileSerializer
from apps.webmails.models import WebMail

logger = logging.getLogger(__name__)


class WebMailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = WebMail
        exclude = ["updated_at"]


class ListWebMailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = WebMail
        exclude = ["updated_at", "username", "password"]


class BulkCreateWebMailSerializer(serializers.ListSerializer):
    """Serializer to handle bulk creation of webmails."""

    def create(self, validated_data):
        # Create multiple WebMail objects at once
        webmails = [WebMail(**data) for data in validated_data]
        webmails_instances = WebMail.objects.bulk_create(webmails)

        logger.debug("Triggering post_save signals")
        for instance in webmails_instances:
            post_save.send(sender=WebMail, instance=instance, created=True)

        logger.info(f"Successfully created {len(webmails_instances)} Webmails")
        return webmails_instances


class CreateWebMailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = WebMail
        exclude = ["status", "is_sold", "location", "hosting"]
        list_serializer_class = BulkCreateWebMailSerializer
