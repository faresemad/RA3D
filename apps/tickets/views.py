import logging

from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.tickets.models import Ticket
from apps.tickets.serializers import CreateTicketSerializer, ListTicketSerializer, RetrieveTicketSerializer
from apps.utils.permissions import IsOwnerOrAdmin, IsSupport

logger = logging.getLogger(__name__)


class TicketViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Ticket.objects.select_related("user").all()
    serializer_class = ListTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateTicketSerializer
        if self.action == "retrieve":
            return RetrieveTicketSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action == "close":
            return [Q(IsAdminUser()) | Q(IsSupport())]
        if self.action == "destroy":
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        logger.info(f"Ticket created by {self.request.user.email}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.mark_as_closed()
        logger.info(f"Ticket closed by {self.request.user.email}")
        return Response(status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(f"Ticket deleted by {self.request.user.email}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_ticket(self, request, pk=None):
        queryset = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
