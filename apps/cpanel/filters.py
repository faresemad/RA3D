from django_filters import rest_framework as filters

from apps.cpanel.models import CPanel


class CPanelFilter(filters.FilterSet):
    class Meta:
        model = CPanel
        fields = {
            "status": ["exact"],
            "tld": ["exact"],
            "cpanel_type": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "created_at": ["exact", "gte", "lte"],
        }
