from django.apps import AppConfig


class WebmailsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.webmails"

    def ready(self):
        import apps.webmails.signals  # noqa
