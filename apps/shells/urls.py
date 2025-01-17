from rest_framework.routers import DefaultRouter

from apps.shells.views import ShellViewSet

router = DefaultRouter()

app_name = "shells"

router.register(r"shell", ShellViewSet, basename="shell")

urlpatterns = router.urls
