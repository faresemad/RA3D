from rest_framework.routers import DefaultRouter

from apps.cpanel.views import CPanelViewSet, LocationsOfCPanelsViewSet, SellerCPanelViewSet

router = DefaultRouter()

app_name = "cpanel"

router.register("seller/cpanel", SellerCPanelViewSet, basename="seller-cpanel")
router.register("locations", LocationsOfCPanelsViewSet, basename="locations")
router.register("cpanel", CPanelViewSet, basename="cpanel")
urlpatterns = router.urls
