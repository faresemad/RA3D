from django.contrib import admin
from django.utils.html import format_html

from apps.sellers.models import SellerRequest


@admin.action(description="Approve selected seller requests")
def approve_requests(modeladmin, request, queryset):
    for seller_request in queryset:
        seller_request.approve()


@admin.action(description="Reject selected seller requests")
def reject_requests(modeladmin, request, queryset):
    for seller_request in queryset:
        seller_request.reject("Bulk rejection")


@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "display_national_id")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "admin_comment")
    readonly_fields = ("id", "created_at")
    actions = [approve_requests, reject_requests]

    @admin.display(description="National ID")
    def display_national_id(self, obj):
        if obj.national_id:
            return format_html(
                "<a href=\"#\" onclick=\"window.open('{}', 'National ID', 'width=600,height=600'); return false;\">View National ID</a>",  # noqa: E501
                obj.national_id.url,
            )
        return "No ID uploaded"

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            if obj.status == SellerRequest.Status.APPROVED:
                obj.approve()
            elif obj.status == SellerRequest.Status.REJECTED:
                obj.reject(obj.admin_comment)
        else:
            super().save_model(request, obj, form, change)
