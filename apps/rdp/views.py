import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rdp.filters import RdpFilter
from apps.rdp.models import Rdp, RdpStatus
from apps.rdp.serializers import (
    BulkCreateRdpTextSerializer,
    BulkUploadRdpSerializer,
    CreateRdpSerializer,
    RdpListSerializer,
    RdpSerializer,
)
from apps.rdp.utils import check_ip_blacklist, check_rdp_port
from apps.utils.permissions import IsOwner, IsSeller

logger = logging.getLogger(__name__)


class SellerRdpViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RdpSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = RdpFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Rdp.objects.filter(user=self.request.user).only(
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
            "details",
            "created_at",
            "is_deleted",
            "hosting",
            "location",
        )
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsSeller()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateRdpSerializer
        elif self.action == "bulk_upload":
            return BulkUploadRdpSerializer
        elif self.action == "bulk_create":
            return BulkCreateRdpTextSerializer
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

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        """Custom action for bulk RDP creation via textarea input"""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Calls bulk_create inside serializer
        return Response({"message": "RDPs created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request, *args, **kwargs):
        """Custom action for bulk RDP creation via file upload"""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Calls bulk_create inside serializer
        return Response({"message": "RDPs created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_as_sold(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_sold()
        logger.info(f"RDP marked as sold by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as sold"})

    @action(detail=True, methods=["post"])
    def mark_as_unsold(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_unsold()
        logger.info(f"RDP marked as unsold by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as unsold"})

    @action(detail=True, methods=["post"])
    def mark_as_delete(self, request, pk=None):
        rdp: Rdp = self.get_object()
        rdp.mark_as_delete()
        logger.info(f"RDP marked as deleted by {request.user.username}")
        return Response({"status": "success", "message": "RDP marked as deleted"})


class RdpViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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
            "created_at",
            "hosting",
            "location",
        )
    )
    serializer_class = RdpListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = RdpFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]

    @action(detail=True, methods=["get"], url_path="check-blacklist")
    def check_blacklist(self, request, pk=None):
        """Check if RDP's IP is blacklisted"""
        rdp_instance = self.get_object()
        results = check_ip_blacklist(rdp_instance.ip)
        return Response(results)

    @action(detail=True, methods=["get"], url_path="check-port")
    def check_ip(self, request, pk=None):
        """Check if RDP's IP is open to RDP port"""
        rdp_instance = self.get_object()
        results = check_rdp_port(rdp_instance.ip)
        return Response({"status": results})
