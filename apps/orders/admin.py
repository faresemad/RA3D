from django.contrib import admin
from django.utils.html import format_html

from apps.orders.models import Order, Transaction


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    list_filter = ("status", "cryptocurrency", "created_at")
    search_fields = ("id", "user__email")
    readonly_fields = ("total_price", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order_link", "cryptocurrency", "amount", "payment_status", "created_at")
    list_filter = ("payment_status", "cryptocurrency", "created_at")
    search_fields = ("transaction_id", "order__id")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    @admin.display(description="Order")
    def order_link(self, obj: Transaction):
        return format_html('<a href="/admin/orders/order/{}">{}</a>', obj.order.id, obj.order)
