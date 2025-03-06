from rest_framework.routers import DefaultRouter

from apps.webmails.views import SellerWebMailViewSet, WebMailViewSet

router = DefaultRouter()

app_name = "webmail"


router.register(r"seller/webmail", SellerWebMailViewSet, basename="seller-webmail")
router.register(r"webmail", WebMailViewSet, basename="webmail")

urlpatterns = router.urls
