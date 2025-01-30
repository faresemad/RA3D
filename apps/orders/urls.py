from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.orders.views import CoinGateWebhookView, OrderViewSet, TransactionViewSet

router = DefaultRouter()
app_name = "orders"
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"transactions", TransactionViewSet, basename="transactions")
urlpatterns = router.urls

urlpatterns += [
    path("webhook/", CoinGateWebhookView.as_view(), name="webhook"),
]
