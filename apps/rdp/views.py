import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rdp.filters import RdpFilter
from apps.rdp.models import Rdp, RdpStatus
from apps.rdp.serializers import CreateRdpSerializer, RdpSerializer
from apps.utils.permissions import IsOwner, IsSeller

logger = logging.getLogger(__name__)


class RdpViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = (
        Rdp.objects.select_related("user")
        .filter(status=RdpStatus.UNSOLD)
        .only(
            "user__username",
            "user__picture",
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
        )
    )
    serializer_class = RdpSerializer
    permission_classes = [IsSeller]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = RdpFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["mark_as_sold", "mark_as_unsold", "mark_as_delete"]:
            return [IsOwner()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateRdpSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"RDP created by {request.user.username}")
        return Response(
            {
                "status": "success",
                "message": "RDP created successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def mark_as_sold(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_sold()
        logger.info(f"RDP marked as sold by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as sold"})

    @action(detail=True, methods=["get"])
    def mark_as_unsold(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_unsold()
        logger.info(f"RDP marked as unsold by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as unsold"})

    @action(detail=True, methods=["get"])
    def mark_as_delete(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_delete()
        logger.info(f"RDP marked as deleted by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as deleted"})
