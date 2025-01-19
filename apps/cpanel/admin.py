from django.contrib import admin
from django.utils import timezone

from apps.cpanel.models import CPanel, CPanelStatus


@admin.register(CPanel)
class CPanelAdmin(admin.ModelAdmin):
    list_display = ("user", "host", "username", "price", "status", "created_at", "updated_at")
    list_filter = ("status", "is_deleted", "cpanel_type", "created_at")
    search_fields = ("user__username", "host", "username")
    readonly_fields = ("status", "is_deleted", "details", "ssl", "tld", "created_at", "updated_at", "deleted_at")
    actions = ["mark_as_sold", "mark_as_unsold", "mark_as_delete"]

    @admin.action(description="Mark selected RDPs as Sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(status=CPanelStatus.SOLD)

    @admin.action(description="Mark selected RDPs as Unsold")
    def mark_as_unsold(self, request, queryset):
        queryset.update(status=CPanelStatus.UNSOLD)

    @admin.action(description="Mark selected RDPs as Deleted")
    def mark_as_delete(self, request, queryset):
        queryset.update(status=CPanelStatus.DELETED, is_deleted=True, deleted_at=timezone.now())
