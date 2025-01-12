from django.contrib import admin

from apps.accounts.models import Account, AccountStatus


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "category",
        "country",
        "type",
        "price",
        "status",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "user__username",
        "category",
        "country",
        "type",
        "price",
        "status",
        "is_sold",
    ]
    list_filter = [
        "user",
        "category",
        "country",
        "type",
        "price",
        "status",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at", "id"]
    actions = ["mark_as_sold"]

    @admin.action(description="Mark selected accounts as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(is_sold=True, status=AccountStatus.SOLD)
