from django.contrib import admin

from apps.wallet.models import Wallet, WithdrawalRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "payment_method", "status", "created_at", "updated_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("user__username", "user__email", "transaction_id", "wallet_address")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("id", "user", "amount", "payment_method", "wallet_address", "status", "transaction_id")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    actions = ["approve_withdrawal_requests", "reject_withdrawal_requests"]

    @admin.action(description="Approve selected withdrawal requests")
    def approve_withdrawal_requests(self, request, queryset):
        for withdrawal in queryset:
            try:
                withdrawal.approve()
                self.message_user(request, f"Successfully approved withdrawal for {withdrawal.user}")
            except Exception as e:
                self.message_user(
                    request, f"Error approving withdrawal for {withdrawal.user}: {str(e)}", level="ERROR"
                )

    @admin.action(description="Reject selected withdrawal requests")
    def reject_withdrawal_requests(self, request, queryset):
        for withdrawal in queryset:
            try:
                withdrawal.reject()
                self.message_user(request, f"Successfully rejected withdrawal for {withdrawal.user}")
            except Exception as e:
                self.message_user(
                    request, f"Error rejecting withdrawal for {withdrawal.user}: {str(e)}", level="ERROR"
                )
