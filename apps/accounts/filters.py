from django_filters import rest_framework as filters

from apps.accounts.models import Account


class AccountFilter(filters.FilterSet):
    class Meta:
        model = Account
        fields = {
            "category__name": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "location": ["exact"],
            "source": ["exact"],
            "created_at": ["exact", "gte", "lte"],
            "website_domain": ["exact"],
        }
