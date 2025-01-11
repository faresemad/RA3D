from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import NotificationViewSet, create_notification, notification_list

app_name = "notifications"

router = DefaultRouter()

router.register(r"received-notifications", NotificationViewSet, basename="received-notifications")
urlpatterns = router.urls
urlpatterns += [
    path("notifications/", notification_list, name="notification_list"),
    path("create-notification/", create_notification, name="create_notification"),
]
