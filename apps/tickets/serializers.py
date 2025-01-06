from rest_framework import serializers

from apps.tickets.models import Ticket


class BaseTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "user", "title", "reason", "created_at"]


class CreateTicketSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        fields = BaseTicketSerializer.Meta.fields + ["message"]


class RetrieveTicketSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        fields = BaseTicketSerializer.Meta.fields + ["message", "status", "closed_at"]


class ListTicketSerializer(BaseTicketSerializer):
    pass
