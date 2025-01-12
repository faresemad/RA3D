from django.contrib import admin

from apps.webmails.models import WebMail, WebMailStatus


@admin.register(WebMail)
class WebMailAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "username",
        "category",
        "niche",
        "price",
        "source",
        "status",
        "created_at",
    ]
    search_fields = [
        "id",
        "user__username",
        "username",
        "category",
        "niche",
        "price",
        "source",
        "status",
    ]
    list_filter = [
        "category",
        "niche",
        "source",
        "status",
        "is_sold",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    actions = ["mark_as_sold", "mark_as_deleted"]
    fieldsets = (
        (None, {"fields": ("id", "user", "username", "password")}),
        ("Details", {"fields": ("category", "niche", "price", "source")}),
        ("Status", {"fields": ("status", "is_sold")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.action(description="Mark selected accounts as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(status=WebMailStatus.SOLD, is_sold=True)

    @admin.action(description="Mark selected accounts as deleted")
    def mark_as_deleted(self, request, queryset):
        queryset.update(status=WebMailStatus.DELETED)
