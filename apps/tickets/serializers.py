# serializers.py
from rest_framework import serializers

from apps.tickets.models import ReasonChoices, StatusChoices, Ticket, TicketResponse


class TicketResponseSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = TicketResponse
        fields = ["id", "user", "message", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_user(self, obj: TicketResponse):
        return obj.user.username if obj.user else None


class BaseTicketSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    reason = serializers.ChoiceField(choices=ReasonChoices.choices)
    status = serializers.ChoiceField(choices=StatusChoices.choices, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "user", "title", "reason", "message", "status"]
        read_only_fields = ["status"]

    def get_user(self, obj: Ticket):
        return obj.user.username if obj.user else None


class TicketDetailsSerializer(BaseTicketSerializer):
    responses = TicketResponseSerializer(many=True, read_only=True)

    class Meta(BaseTicketSerializer.Meta):
        fields = BaseTicketSerializer.Meta.fields + ["responses"]


class TicketListSerializer(BaseTicketSerializer):
    pass
