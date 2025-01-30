# serializers.py
from rest_framework import serializers

from apps.tickets.models import ReasonChoices, StatusChoices, Ticket, TicketResponse


class TicketResponseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TicketResponse
        fields = ["id", "user", "message", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class TicketSerializer(serializers.ModelSerializer):
    responses = TicketResponseSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    reason = serializers.ChoiceField(choices=ReasonChoices.choices)
    status = serializers.ChoiceField(choices=StatusChoices.choices, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "user", "title", "reason", "message", "status", "closed_at", "created_at", "responses"]
        read_only_fields = ["status", "closed_at", "created_at"]
