import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.leads.filters import LeadsFilter
from apps.leads.models import Leads, LeadsCategory, LeadsData
from apps.leads.serializers import CategorySerializer, CreateLeadsDataSerializer, LeadsSerializer

logger = logging.getLogger(__name__)


class LeadsDataViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LeadsData.objects.all()
    serializer_class = CreateLeadsDataSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Leads data created successfully.")
        return Response({"message": "Leads created successfully."}, status=status.HTTP_201_CREATED)


class LeadsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Leads.objects.select_related("user", "category")
        .filter(is_sold=False)
        .only(
            "user__username",
            "user__picture",
            "category__name",
            "location",
            "description",
            "niche",
            "website_domain",
            "provider",
            "password",
            "emails_number",
            "proof",
            "price",
            "created_at",
            "is_sold",
        )
    )
    serializer_class = LeadsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = LeadsFilter
    ordering_fields = ["created_at"]
    search_fields = ["category", "price", "user", "location", "is_sold", "created_at", "website_domain"]


class LeadsCategoryViewSet(viewsets.ModelViewSet):
    queryset = LeadsCategory.objects.all().order_by("-created_at")
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("Leads category created successfully.")
        return Response({"message": "Leads category created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        logger.info("Leads category updated successfully.")
        return Response({"message": "Leads category updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        logger.info("Leads category deleted successfully.")
        return Response({"message": "Leads category deleted successfully."}, status=status.HTTP_200_OK)
