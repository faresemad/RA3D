from django.contrib import admin

from apps.users.models import ActivationCode, CustomUserProfile


@admin.register(CustomUserProfile)
class CustomUserProfileAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "first_name", "last_name", "status", "submitted_at", "is_active", "is_staff"]
    search_fields = ["email", "username", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff"]

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


admin.site.register(ActivationCode)
