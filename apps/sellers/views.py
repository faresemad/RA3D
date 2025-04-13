import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.permissions import IsAccountAdmin

from apps.sellers.filters import SellerRequestFilter
from apps.sellers.models import SellerRequest
from apps.sellers.serializers import (
    ListSellerRequestSerializer,
    SellerRequestAdminUpdateSerializer,
    SellerRequestCreateSerializer,
    SellerRequestDetailSerializer,
)

logger = logging.getLogger(__name__)


class SellerRequestViewSet(viewsets.ModelViewSet):
    queryset = SellerRequest.objects.select_related("user").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SellerRequestFilter

    def get_permissions(self):
        logger.info(f"Checking permissions for action: {self.action}")
        if self.action in ["list", "update", "partial_update"]:
            return [IsAccountAdmin()]
        elif self.action in ["approve", "reject"]:
            return [IsAccountAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        logger.info(f"Getting serializer class for action: {self.action}")
        if self.action == "create":
            return SellerRequestCreateSerializer
        elif self.action == "list":
            return ListSellerRequestSerializer
        elif self.action in ["update", "partial_update"]:
            return SellerRequestAdminUpdateSerializer
        return SellerRequestDetailSerializer

    def get_queryset(self):
        logger.info(f"Getting queryset for user: {self.request.user}")
        if self.request.user.is_staff or self.request.user.status == self.request.user.AccountStatus.ADMIN:
            return SellerRequest.objects.all()
        return SellerRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        logger.info(f"Creating seller request for user: {self.request.user}")
        if SellerRequest.objects.filter(user=self.request.user).exists():
            logger.warning(f"Duplicate seller request attempt by user: {self.request.user}")
            raise serializers.ValidationError("You have already submitted a seller request.")
        serializer.save(user=self.request.user)
        logger.info(f"Successfully created seller request for user: {self.request.user}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def approve(self, request, pk=None):
        logger.info(f"Approving seller request with ID: {pk}")
        seller_request = self.get_object()
        seller_request.approve()
        logger.info(f"Seller request with ID: {pk} approved")
        return Response({"status": "approved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def reject(self, request, pk=None):
        logger.info(f"Rejecting seller request with ID: {pk}")
        seller_request = self.get_object()
        seller_request.reject(comment="Rejected by admin")
        logger.info(f"Seller request with ID: {pk} rejected")
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)
