from django.apps import AppConfig


class CpanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cpanel"

    def ready(self):
        import apps.cpanel.signals  # noqa
