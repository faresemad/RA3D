from django.contrib import admin
from django.utils import timezone

from apps.tickets.models import StatusChoices, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "reason", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "user__username")
    readonly_fields = ("id", "created_at")
    actions = ["mark_as_opened", "mark_as_closed"]

    @admin.action(description="Mark selected tickets as opened")
    def mark_as_opened(self, request, queryset):
        queryset.update(status=StatusChoices.OPENED)

    @admin.action(description="Mark selected tickets as closed")
    def mark_as_closed(self, request, queryset):
        queryset.update(status=StatusChoices.CLOSED, closed_at=timezone.now())
