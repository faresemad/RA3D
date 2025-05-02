# views.py
import logging

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tickets.models import Ticket, TicketResponse
from apps.tickets.permissions import IsOwnerOrStaff, IsTicketParticipantOrStaff
from apps.tickets.serializers import TicketDetailsSerializer, TicketListSerializer, TicketResponseSerializer

logger = logging.getLogger(__name__)


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TicketDetailsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        queryset = Ticket.objects.select_related("user").prefetch_related("responses__user")

        is_staff_or_support = (
            self.request.user.status in ["SUPPORT", "ADMIN"]
            or self.request.user.is_staff
            or self.request.user.is_superuser
        )

        if is_staff_or_support:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketDetailsSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        logger.info(f"Ticket {serializer.instance.id} created by {self.request.user}")

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.mark_as_closed()
        logger.info(f"Ticket {ticket.id} closed by {request.user}")
        return Response({"status": "Ticket closed"})

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        ticket.mark_as_opened()
        logger.info(f"Ticket {ticket.id} reopened by {request.user}")
        return Response({"status": "Ticket reopened"})


class TicketResponseViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TicketResponseSerializer
    permission_classes = [IsAuthenticated, IsTicketParticipantOrStaff]

    def get_queryset(self):
        return TicketResponse.objects.select_related("user", "ticket").filter(ticket_id=self.kwargs["ticket_pk"])

    def perform_create(self, serializer):
        ticket = Ticket.objects.get(pk=self.kwargs["ticket_pk"])
        serializer.save(user=self.request.user, ticket=ticket)
        logger.info(f"Response added to ticket {ticket.id} by {self.request.user}")
