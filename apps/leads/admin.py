from django.contrib import admin

from apps.leads.models import Leads, LeadsCategory, LeadsData


@admin.register(LeadsCategory)
class LeadsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]


class LeadsDataInline(admin.TabularInline):
    model = LeadsData


@admin.register(Leads)
class LeadsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "category",
        "website_domain",
        "location",
        "price",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    search_fields = ["user", "category", "website_domain", "location", "price", "is_sold"]
    list_filter = [
        "user",
        "category",
        "website_domain",
        "location",
        "price",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at", "is_sold"]
    actions = ["mark_as_sold"]
    inlines = [LeadsDataInline]

    @admin.action(description="Mark selected accounts as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(is_sold=True)
