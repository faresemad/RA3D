from rest_framework.routers import DefaultRouter

from apps.rdp.views import RdpViewSet

router = DefaultRouter()

app_name = "rdp"

router.register(r"rdp", RdpViewSet, basename="rdp")

urlpatterns = router.urls
