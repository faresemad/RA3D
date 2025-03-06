import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.utils.permissions import IsSeller
from apps.webmails.filters import WebMailFilter
from apps.webmails.models import WebMail
from apps.webmails.serializers import (
    BulkCreateWebMailTextSerializer,
    BulkUploadWebMailSerializer,
    CreateWebMailSerializer,
    ListWebMailSerializer,
    WebMailSerializer,
)

logger = logging.getLogger(__name__)


class SellerWebMailViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = (
        WebMail.objects.select_related("user")
        .filter(is_sold=False)
        .only(
            "id",
            "user__username",
            "user__picture",
            "domain",
            "price",
            "username",
            "password",
            "source",
            "category",
            "niche",
            "status",
            "is_sold",
            "created_at",
        )
    )
    serializer_class = WebMailSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = WebMailFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user__username", "domain"]

    def get_queryset(self):
        queryset = (
            WebMail.objects.select_related("user")
            .filter(is_sold=False)
            .only(
                "id",
                "user__username",
                "user__picture",
                "domain",
                "price",
                "username",
                "password",
                "hosting",
                "location",
                "source",
                "category",
                "niche",
                "status",
                "is_sold",
                "created_at",
            )
        )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateWebMailSerializer
        elif self.action == "bulk_create":
            return BulkCreateWebMailTextSerializer
        elif self.action == "bulk_upload":
            return BulkUploadWebMailSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"WebMail created by {request.user.username} with id {serializer.instance.id}")
        return Response(
            {"status": "success", "message": "WebMail created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        serializer = BulkCreateWebMailTextSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "WebMail created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request, *args, **kwargs):
        serializer = BulkUploadWebMailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "WebMail uploaded successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_as_sold(self, request, pk=None):
        webmail = self.get_object()
        webmail.mark_as_sold()
        return Response({"status": "webmail marked as sold"})

    @action(detail=True, methods=["post"])
    def mark_as_unsold(self, request, pk=None):
        webmail = self.get_object()
        webmail.mark_as_unsold()
        return Response({"status": "webmail marked as unsold"})

    @action(detail=True, methods=["post"])
    def mark_as_deleted(self, request, pk=None):
        webmail = self.get_object()
        webmail.mark_as_deleted()
        return Response({"status": "webmail marked as deleted"})


class WebMailViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        WebMail.objects.select_related("user")
        .filter(is_sold=False)
        .only(
            "id",
            "user__username",
            "user__picture",
            "domain",
            "hosting",
            "location",
            "price",
            "source",
            "category",
            "niche",
            "status",
            "is_sold",
            "created_at",
        )
    )
    serializer_class = ListWebMailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = WebMailFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user__username", "domain"]
