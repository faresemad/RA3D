from rest_framework.routers import DefaultRouter

from apps.sellers.views import SellerRequestViewSet

app_name = "sellers"

router = DefaultRouter()
router.register(r"seller-requests", SellerRequestViewSet, basename="seller-request")

urlpatterns = router.urls
