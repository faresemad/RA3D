from django_filters import rest_framework as filters

from apps.business.models import Business


class BusinessFilter(filters.FilterSet):
    class Meta:
        model = Business
        fields = {
            "category__name": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "location": ["exact"],
            "source": ["exact"],
            "created_at": ["exact", "gte", "lte"],
            "website_domain": ["exact"],
        }
