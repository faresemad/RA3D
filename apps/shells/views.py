import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shells.filters import ShellFilter
from apps.shells.models import Shell, ShellStatus
from apps.shells.serializers import (
    BulkCreateShellTextSerializer,
    BulkUploadShellSerializer,
    CreateShellSerializer,
    ShellListSerializer,
    ShellSerializer,
)
from apps.utils.permissions import IsOwner, IsSeller

logger = logging.getLogger(__name__)


class SellerShellViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ShellSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ShellFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]

    def get_queryset(self):
        queryset = Shell.objects.filter(status=ShellStatus.UNSOLD).only(
            "shell_url",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
            "is_deleted",
        )
        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsSeller()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateShellSerializer
        elif self.action == "bulk_create":
            return BulkCreateShellTextSerializer
        elif self.action == "bulk_upload":
            return BulkUploadShellSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"Shell created by {request.user.username}")
        return Response(
            {
                "status": "success",
                "message": "Shell created successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        serializer = BulkCreateShellTextSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Shells created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request, *args, **kwargs):
        serializer = BulkUploadShellSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Shells uploaded successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_sold(self, request, pk=None):
        shell = self.get_object()
        shell.mark_as_sold()
        logger.info(f"Shell marked as sold by {request.user.username}")
        return Response({"status": "success", "message": "Shell marked as sold"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_unsold(self, request, pk=None):
        shell = self.get_object()
        shell.mark_as_unsold()
        logger.info(f"Shell marked as unsold by {request.user.username}")
        return Response({"status": "success", "message": "Shell marked as unsold"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_delete(self, request, pk=None):
        shell = self.get_object()
        shell.mark_as_delete()
        logger.info(f"Shell marked as deleted by {request.user.username}")
        return Response({"status": "success", "message": "Shell marked as deleted"})


class ShellViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Shell.objects.select_related("user")
        .filter(status=ShellStatus.UNSOLD)
        .only(
            "user__username",
            "user__picture",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
        )
    )
    serializer_class = ShellListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ShellFilter
    ordering_fields = ["created_at"]
    search_fields = ["tld", "user__username"]
