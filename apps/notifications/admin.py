from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "truncated_message", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]

    @admin.display(description="Message")
    def truncated_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    @admin.action(description="Mark selected notifications as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected notifications as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    fieldsets = (
        ("Notification Details", {"fields": ("id", "user", "message", "is_read")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
