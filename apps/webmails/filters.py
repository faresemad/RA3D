from django_filters import rest_framework as filters

from apps.webmails.models import WebMail


class WebMailFilter(filters.FilterSet):
    class Meta:
        model = WebMail
        fields = {
            "category": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "source": ["exact"],
            "created_at": ["exact", "gte", "lte"],
            "niche": ["exact"],
            "status": ["exact"],
        }
