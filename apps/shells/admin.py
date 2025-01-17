from django.contrib import admin
from django.utils import timezone

from apps.shells.models import Shell, ShellStatus


@admin.register(Shell)
class ShellAdmin(admin.ModelAdmin):
    list_display = ("user", "shell_url", "shell_type", "status", "price", "is_deleted")
    list_filter = ("shell_type", "status", "is_deleted", "created_at", "updated_at")
    search_fields = ("shell_url", "user__username")
    readonly_fields = ("status", "created_at", "updated_at", "deleted_at", "is_deleted", "ssl", "tld", "details")
    actions = ["mark_as_sold", "mark_as_unsold", "mark_as_delete"]

    @admin.action(description="Mark selected shells as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(status=ShellStatus.SOLD)

    @admin.action(description="Mark selected shells as unsold")
    def mark_as_unsold(self, request, queryset):
        queryset.update(status=ShellStatus.UNSOLD)

    @admin.action(description="Mark selected shells as deleted")
    def mark_as_delete(self, request, queryset):
        queryset.update(status=ShellStatus.DELETED, is_deleted=True, deleted_at=timezone.now())
