from django.contrib import admin, messages

from apps.users.models import ActivationCode, CustomUserProfile


@admin.register(CustomUserProfile)
class CustomUserProfileAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "first_name", "last_name", "status", "submitted_at", "is_active", "is_staff"]
    search_fields = ["email", "username", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "status"]
    actions = ["mark_as_admin", "mark_as_seller", "mark_as_support", "mark_as_buyer"]

    fieldsets = (
        (None, {"fields": ("email", "username", "status")}),
        ("Personal info", {"fields": ("first_name", "last_name", "picture")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "email_confirmed", "email_verification_code")},
        ),
        ("Important dates", {"fields": ("last_login", "submitted_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("submitted_at", "last_login", "password")

    @admin.action(description="Mark selected users as Admin")
    def mark_as_admin(self, request, queryset):
        queryset.update(is_staff=True, is_superuser=True)
        messages.success(request, "Selected users were marked as Admin")

    @admin.action(description="Mark selected users as Seller")
    def mark_as_seller(self, request, queryset):
        queryset.update(status=CustomUserProfile.AccountStatus.SELLER)
        messages.success(request, "Selected users were marked as Seller")

    @admin.action(description="Mark selected users as Support")
    def mark_as_support(self, request, queryset):
        queryset.update(status=CustomUserProfile.AccountStatus.SUPPORT)
        messages.success(request, "Selected users were marked as Support")

    @admin.action(description="Mark selected users as Buyer")
    def mark_as_buyer(self, request, queryset):
        queryset.update(status=CustomUserProfile.AccountStatus.BUYER)
        messages.success(request, "Selected users were marked as Buyer")


admin.site.register(ActivationCode)
