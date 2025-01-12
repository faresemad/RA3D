from rest_framework.routers import DefaultRouter

from apps.webmails.views import WebMailViewSet

router = DefaultRouter()

app_name = "webmail"

router.register(r"webmail", WebMailViewSet, basename="webmail")

urlpatterns = router.urls
