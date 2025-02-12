from django.apps import AppConfig


class RdpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rdp"

    def ready(self):
        import apps.rdp.signals  # noqa
