from django_filters import rest_framework as filters

from apps.rdp.models import Rdp


class RdpFilter(filters.FilterSet):
    class Meta:
        model = Rdp
        fields = {
            "status": ["exact"],
            "windows_type": ["exact"],
            "access_type": ["exact"],
            "price": ["exact", "gte", "lte"],
            "ram_size": ["exact", "gte", "lte"],
            "cpu_cores": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "created_at": ["exact", "gte", "lte"],
        }
