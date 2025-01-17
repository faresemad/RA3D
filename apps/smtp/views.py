import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.smtp.filters import SmtpFilter
from apps.smtp.models import SMTP, SmtpStatus
from apps.smtp.serializers import CreateSmtpSerializer, SmtpSerializer
from apps.utils.permissions import IsSeller

logger = logging.getLogger(__name__)


class SmtpViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = (
        SMTP.objects.select_related("user")
        .filter(status=SmtpStatus.UNSOLD)
        .only(
            "user__username",
            "user__picture",
            "ip",
            "port",
            "smtp_type",
            "status",
            "price",
            "created_at",
        )
    )
    serializer_class = SmtpSerializer
    permission_classes = [IsSeller]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = SmtpFilter
    ordering_fields = ["created_at"]
    search_fields = ["port", "ip", "user__username"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateSmtpSerializer
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
