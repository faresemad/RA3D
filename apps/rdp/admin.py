from django.contrib import admin
from django.utils import timezone

from apps.rdp.models import Rdp, RdpStatus


@admin.register(Rdp)
class RdpAdmin(admin.ModelAdmin):
    list_display = ("user", "ip", "username", "price", "status", "created_at", "updated_at")
    list_filter = ("status", "windows_type", "rdp_type", "created_at")
    search_fields = ("user__username", "ip", "username")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    actions = ["mark_as_sold", "mark_as_unsold", "mark_as_delete"]

    @admin.action(description="Mark selected RDPs as Sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(status=RdpStatus.SOLD)

    @admin.action(description="Mark selected RDPs as Unsold")
    def mark_as_unsold(self, request, queryset):
        queryset.update(status=RdpStatus.UNSOLD)

    @admin.action(description="Mark selected RDPs as Deleted")
    def mark_as_delete(self, request, queryset):
        queryset.update(status=RdpStatus.DELETED, is_deleted=True, deleted_at=timezone.now())
