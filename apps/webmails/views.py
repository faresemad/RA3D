import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.utils.permissions import IsSeller
from apps.webmails.filters import WebMailFilter
from apps.webmails.models import WebMail
from apps.webmails.serializers import CreateWebMailSerializer, WebMailSerializer

logger = logging.getLogger(__name__)


class WebMailViewSet(viewsets.ModelViewSet):
    queryset = (
        WebMail.objects.select_related("user")
        .filter(is_sold=False)
        .only(
            "id",
            "user__username",
            "user__picture",
            "domain",
            "price",
            "source",
            "category",
            "niche",
            "status",
            "is_sold",
            "created_at",
        )
    )
    serializer_class = WebMailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = WebMailFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user__username", "domain"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateWebMailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "create":
            return [IsSeller()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"WebMail created by {request.user.username} with id {serializer.instance.id}")
        return Response(
            {"status": "success", "message": "WebMail created successfully"},
            status=status.HTTP_201_CREATED,
        )
