from django.contrib import admin

from apps.business.models import Business, BusinessCategory, BusinessData


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]


class BusinessDataInline(admin.TabularInline):
    model = BusinessData


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
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
    readonly_fields = ["created_at", "updated_at", "is_sold"]
    actions = ["mark_as_sold"]
    inlines = [BusinessDataInline]

    @admin.action(description="Mark selected accounts as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(is_sold=True)
