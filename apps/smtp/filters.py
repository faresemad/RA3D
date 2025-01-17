from django_filters import rest_framework as filters

from apps.smtp.models import SMTP


class SmtpFilter(filters.FilterSet):
    class Meta:
        model = SMTP
        fields = {
            "smtp_type": ["exact"],
            "price": ["exact", "gte", "lte"],
            "user__username": ["exact"],
            "created_at": ["exact", "gte", "lte"],
        }
