import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.smtp.filters import SmtpFilter
from apps.smtp.models import SMTP, SmtpStatus
from apps.smtp.serializers import (
    BulkCreateSMTPTextSerializer,
    BulkUploadSMTPSerializer,
    CreateSmtpSerializer,
    SmtpListSerializer,
    SmtpSerializer,
)
from apps.utils.permissions import IsOwner, IsSeller

logger = logging.getLogger(__name__)


class SellerSmtpViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SmtpSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = SmtpFilter
    ordering_fields = ["created_at"]
    search_fields = ["port", "ip", "user__username"]

    def get_queryset(self):
        queryset = SMTP.objects.only(
            "ip",
            "port",
            "username",
            "password",
            "hosting",
            "location",
            "smtp_type",
            "status",
            "price",
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
            return CreateSmtpSerializer
        elif self.action == "bulk_create":
            return BulkCreateSMTPTextSerializer
        elif self.action == "bulk_upload":
            return BulkUploadSMTPSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"SMTP created by {request.user.username}")
        return Response(
            {
                "status": "success",
                "message": "SMTP created successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        serializer = BulkCreateSMTPTextSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Shells created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request, *args, **kwargs):
        serializer = BulkUploadSMTPSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Shells uploaded successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_as_sold(self, request, pk=None):
        smtp = self.get_object()
        smtp.mark_as_sold()
        return Response({"status": "smtp marked as sold"})

    @action(detail=True, methods=["post"])
    def mark_as_unsold(self, request, pk=None):
        smtp = self.get_object()
        smtp.mark_as_unsold()
        return Response({"status": "smtp marked as unsold"})

    @action(detail=True, methods=["post"])
    def mark_as_deleted(self, request, pk=None):
        smtp = self.get_object()
        smtp.mark_as_deleted()
        return Response({"status": "smtp marked as deleted"})


class SmtpViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        SMTP.objects.select_related("user")
        .filter(status=SmtpStatus.UNSOLD)
        .only(
            "user__username",
            "user__picture",
            "ip",
            "username",
            "hosting",
            "location",
            "port",
            "smtp_type",
            "status",
            "price",
            "created_at",
        )
    )
    serializer_class = SmtpListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = SmtpFilter
    ordering_fields = ["created_at"]
    search_fields = ["port", "ip", "user__username"]


class LocationsOfSmtpViewSet(viewsets.ViewSet):
    """
    ViewSet to get all locations of SMTPs.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        locations = (
            SMTP.objects.filter(status=SmtpStatus.UNSOLD, location__isnull=False)
            .values_list("location", flat=True)
            .distinct()
        )
        return Response(locations)
