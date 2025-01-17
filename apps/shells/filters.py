from django_filters import rest_framework as filters

from apps.shells.models import Shell


class ShellFilter(filters.FilterSet):
    class Meta:
        model = Shell
        fields = {
            "shell_type": ["exact"],
            "tld": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "created_at": ["exact", "gte", "lte"],
        }
