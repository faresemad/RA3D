from django.contrib import admin

from apps.accounts.models import Account, AccountCategory, AccountData


@admin.register(AccountCategory)
class AccountCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]


class AccountDataInline(admin.TabularInline):
    model = AccountData


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "category",
        "website_domain",
        "location",
        "price",
        "source",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    search_fields = ["user", "category", "website_domain", "location", "price", "source", "is_sold"]
    list_filter = [
        "user",
        "category",
        "website_domain",
        "location",
        "price",
        "source",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["mark_as_sold"]
    inlines = [AccountDataInline]

    @admin.action(description="Mark selected accounts as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(is_sold=True)
