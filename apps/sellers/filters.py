import django_filters

from apps.sellers.models import SellerRequest


class SellerRequestFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = SellerRequest
        fields = ["status", "created_at"]
