import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.business.filters import BusinessFilter
from apps.business.models import Business, BusinessCategory, BusinessData
from apps.business.serializers import BusinessSerializer, CategorySerializer, CreateBusinessDataSerializer

logger = logging.getLogger(__name__)


class BusinessDataViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = BusinessData.objects.all()
    serializer_class = CreateBusinessDataSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Business data created successfully.")
        return Response({"message": "Business created successfully."}, status=status.HTTP_201_CREATED)


class BusinessViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Business.objects.select_related("user", "category")
        .filter(is_sold=False)
        .only(
            "user__username",
            "user__picture",
            "category__name",
            "location",
            "source",
            "website_domain",
            "host",
            "price",
            "type",
            "niche",
            "created_at",
            "is_sold",
        )
    )
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = BusinessFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user", "location", "source", "is_sold", "created_at", "website_domain"]


class BusinessCategoryViewSet(viewsets.ModelViewSet):
    queryset = BusinessCategory.objects.all().order_by("-created_at")
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Business category created successfully.")
        return Response({"message": "Business category created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        logger.info("Business category updated successfully.")
        return Response({"message": "Business category updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        logger.info("Business category deleted successfully.")
        return Response({"message": "Business category deleted successfully."}, status=status.HTTP_200_OK)
