import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.cpanel.filters import CPanelFilter
from apps.cpanel.models import CPanel, CPanelStatus
from apps.cpanel.serializers import (
    BulkCreateCPanelTextSerializer,
    BulkUploadCPanelSerializer,
    CreateCPanelSerializer,
    OwnerCPanelSerializer,
    UserCPanelSerializer,
)
from apps.cpanel.utils import check_cpanel_status
from apps.utils.permissions import IsOwner, IsSeller

logger = logging.getLogger(__name__)


class SellerCPanelViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = OwnerCPanelSerializer
    permission_classes = [IsOwner, IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CPanelFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = CPanel.objects.filter(user=self.request.user).only(
            "host",
            "username",
            "password",
            "price",
            "cpanel_type",
            "status",
            "ssl",
            "tld",
            "details",
            "hosting",
            "location",
            "created_at",
        )
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsSeller]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateCPanelSerializer
        elif self.action == "bulk_create":
            return BulkCreateCPanelTextSerializer
        elif self.action == "bulk_upload":
            return BulkUploadCPanelSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"CPanel created by {request.user.username}")
        return Response(
            {
                "status": "success",
                "message": "CPanel created successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        """
        Bulk create cPanel from textarea input.

        Input Format:
            host | username | password | price | cpanel_type

        Rules:
        - Each field should be separated by ' | '
        - Each account entry should be on a new line
        - All fields are required
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Bulk CPanel created by {request.user.username}")
        return Response(
            {"status": "success", "message": "cPanels created successfully!"}, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request, *args, **kwargs):
        """Custom action for bulk cPanel creation via file upload"""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"status": "success", "message": "cPanels created successfully!"}, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def mark_as_sold(self, request, pk=None):
        cpanel = self.get_object()
        cpanel.mark_as_sold()
        logger.info(f"CPanel marked as sold by {request.user.username}")
        return Response({"status": "success", "message": "CPanel marked as sold"})

    @action(detail=True, methods=["post"])
    def mark_as_unsold(self, request, pk=None):
        cpanel = self.get_object()
        cpanel.mark_as_unsold()
        logger.info(f"CPanel marked as unsold by {request.user.username}")
        return Response({"status": "success", "message": "CPanel marked as unsold"})

    @action(detail=True, methods=["post"])
    def mark_as_delete(self, request, pk=None):
        cpanel = self.get_object()
        cpanel.mark_as_delete()
        logger.info(f"CPanel marked as deleted by {request.user.username}")
        return Response({"status": "success", "message": "CPanel marked as deleted"})


class CPanelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        CPanel.objects.select_related("user")
        .filter(status=CPanelStatus.UNSOLD)
        .only(
            "user__username",
            "user__picture",
            "username",
            "price",
            "ssl",
            "tld",
            "cpanel_type",
            "status",
            "created_at",
            "hosting",
            "location",
        )
    )
    serializer_class = UserCPanelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CPanelFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]

    @action(detail=True, methods=["get"], url_path="check-status")
    def check_status(self, request, pk=None):
        cpanel = self.get_object()
        status = check_cpanel_status(cpanel.host)
        return Response(status)
