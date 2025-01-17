from django.contrib import admin

from apps.smtp.models import SMTP


@admin.register(SMTP)
class SMTPAdmin(admin.ModelAdmin):
    list_display = ("user", "ip", "port", "username", "smtp_type", "status", "price", "is_deleted")
    list_filter = ("smtp_type", "status", "is_deleted", "created_at", "updated_at")
    search_fields = ("ip", "username", "user__username")
    readonly_fields = ("status", "created_at", "updated_at", "is_deleted", "deleted_at")
