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


# JAZZMIN SETTINGS
# -----------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Ra3d Admin",
    "site_header": "Ra3d",
    "site_brand": "Ra3d",
    # "site_logo": "icons/icon.ico",
    # "login_logo": "icons/icon.ico",
    # "login_logo_dark": "icons/icon.ico",
    # "site_logo_classes": "img-circle",
    # "site_icon": "icons/icon.ico",
    "welcome_sign": "Welcome to the Ra3d Admin Panel",
    "copyright": "Fares Emad (Scorpion)",
    "search_model": ["auth.User"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "GitHub", "url": "https://github.com/faresemad", "new_window": True},
        {"model": "users.student"},
        {
            "app": "users",
        },
    ],
    "usermenu_links": [
        {"name": "GitHib", "url": "https://github.com/faresemad", "new_window": True},
        {
            "name": "Facebook",
            "url": "https://www.facebook.com/faresemadx",
            "new_window": True,
        },
        {
            "name": "Instagram",
            "url": "https://www.instagram.com/faresemadx",
            "new_window": True,
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/faresemad/",
            "new_window": True,
        },
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": ["auth.Group", "auth.Permission", "sites"],
    "hide_models": ["auth.Group", "auth.Permission", "sites"],
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],
    "custom_links": {
        "books": [
            {
                "name": "Make Messages",
                "url": "make_messages",
                "icon": "fas fa-comments",
                "permissions": ["books.view_book"],
            }
        ]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "css/main.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-gray navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
