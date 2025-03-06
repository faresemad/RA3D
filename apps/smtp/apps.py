from django.apps import AppConfig


class SmtpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.smtp"

    def ready(self):
        import apps.smtp.signals  # noqa
