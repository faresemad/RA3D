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
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB

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
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "https://api.ra3d.store",
    "http://api.ra3d.store",
    "https://coingate.com",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://api.ra3d.store",
    "http://api.ra3d.store",
    "https://coingate.com",
]
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
