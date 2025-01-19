from rest_framework.routers import DefaultRouter

from apps.cpanel.views import CPanelViewSet

router = DefaultRouter()

app_name = "cpanel"

router.register("cpanel", CPanelViewSet, basename="cpanel")
urlpatterns = router.urls
