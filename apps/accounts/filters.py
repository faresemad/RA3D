from django_filters import rest_framework as filters

from apps.accounts.models import Account


class AccountFilter(filters.FilterSet):
    class Meta:
        model = Account
        fields = {
            "category": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "created_at": ["exact", "gte", "lte"],
        }
