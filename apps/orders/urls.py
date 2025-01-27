from rest_framework.routers import DefaultRouter

from apps.orders.views import OrderViewSet

router = DefaultRouter()
app_name = "orders"
router.register(r"orders", OrderViewSet, basename="orders")
urlpatterns = router.urls
