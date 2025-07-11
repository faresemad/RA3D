from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# API patterns for Admin
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API patterns for Local Apps
urlpatterns += [
    path(f"{settings.API_PREFIX}oauth/", include("apps.users.api.urls", namespace="users")),
    path(f"{settings.API_PREFIX}dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path(f"{settings.API_PREFIX}tickets/", include("apps.tickets.urls", namespace="tickets")),
    path(f"{settings.API_PREFIX}accounts/", include("apps.accounts.urls", namespace="accounts")),
    path(f"{settings.API_PREFIX}webmail/", include("apps.webmails.urls", namespace="webmail")),
    path(f"{settings.API_PREFIX}smtp/", include("apps.smtp.urls", namespace="smtp")),
    path(f"{settings.API_PREFIX}shells/", include("apps.shells.urls", namespace="shells")),
    path(f"{settings.API_PREFIX}rdp/", include("apps.rdp.urls", namespace="rdp")),
    path(f"{settings.API_PREFIX}cpanel/", include("apps.cpanel.urls", namespace="cpanel")),
    path(f"{settings.API_PREFIX}notifications/", include("apps.notifications.urls", namespace="notifications")),
    path(f"{settings.API_PREFIX}orders/", include("apps.orders.urls", namespace="orders")),
    path(f"{settings.API_PREFIX}wallet/", include("apps.wallet.urls", namespace="wallet")),
    path(f"{settings.API_PREFIX}sellers/", include("apps.sellers.urls", namespace="sellers")),
]

# API patterns for Spectacular
urlpatterns += [
    path(f"{settings.API_PREFIX}schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        f"{settings.API_PREFIX}docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)

# Catch-all pattern for invalid URLs
# urlpatterns += [
#     path("<path:invalid_path>", TemplateView.as_view(template_name="index.html"), name="404"),
# ]
