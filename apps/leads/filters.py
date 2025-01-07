from django_filters import rest_framework as filters

from apps.leads.models import Leads


class LeadsFilter(filters.FilterSet):
    class Meta:
        model = Leads
        fields = {
            "category__name": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "location": ["exact"],
            "created_at": ["exact", "gte", "lte"],
            "website_domain": ["exact"],
        }
