from .base import *  # noqa
from .base import INSTALLED_APPS, MIDDLEWARE, env

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

ADMIN_URL = env.str("ADMIN_URL", default="admin/")

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

# Email settings
# ----------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp4dev"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "noreply@example.com"

DESCRIPTION = """
# Ra3d Platform

A platform for selling social media services, accounts, SSH, and other services.

## Developer

Developed by [Fares Emad](https://github.com/faresemad)

## More Information

Visit our [GitHub Repository](https://github.com/faresemad/RA3D) for documentation, updates, and contribution guidelines.
"""  # noqa

SPECTACULAR_SETTINGS = {
    "TITLE": "Ra3d API",
    "DESCRIPTION": DESCRIPTION,
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

SILENCED_SYSTEM_CHECKS = ["drf_spectacular.W001", "drf_spectacular.W002", "fields.W340", "staticfiles.W004"]

# In Deployment
# -----------------------------------------------------------------
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
