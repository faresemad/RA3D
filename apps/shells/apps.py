from django.apps import AppConfig


class ShellsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shells"

    def ready(self):
        import apps.shells.signals  # noqa
