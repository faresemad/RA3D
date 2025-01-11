# serializers.py

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "created_at", "is_read"]
        read_only_fields = ["id", "created_at"]

    def validate_message(self, value):
        """Custom validation for message field."""
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        return value
