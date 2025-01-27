from rest_framework.routers import DefaultRouter

from apps.shells.views import SellerShellViewSet, ShellViewSet

router = DefaultRouter()

app_name = "shells"

router.register(r"seller/shell", SellerShellViewSet, basename="seller-shell")
router.register(r"shell", ShellViewSet, basename="shell")

urlpatterns = router.urls
