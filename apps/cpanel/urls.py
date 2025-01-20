from rest_framework.routers import DefaultRouter

from apps.cpanel.views import CPanelViewSet, SellerCPanelViewSet

router = DefaultRouter()

app_name = "cpanel"

router.register("sell-cpanel", SellerCPanelViewSet, basename="sell-cpanel")
router.register("cpanel", CPanelViewSet, basename="cpanel")
urlpatterns = router.urls
