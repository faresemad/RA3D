from rest_framework.routers import DefaultRouter

from apps.webmails.views import LocationsOfWebmailViewSet, SellerWebMailViewSet, WebMailViewSet

router = DefaultRouter()

app_name = "webmail"


router.register(r"locations", LocationsOfWebmailViewSet, basename="webmail-locations")
router.register(r"seller/webmail", SellerWebMailViewSet, basename="seller-webmail")
router.register(r"webmail", WebMailViewSet, basename="webmail")

urlpatterns = router.urls
