from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.orders.views import (
    CoinGateWebhookView,
    OrderViewSet,
    PaymentCancelView,
    PaymentSuccessView,
    PlisioWebhookView,
    TransactionViewSet,
)

router = DefaultRouter()
app_name = "orders"
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"transactions", TransactionViewSet, basename="transactions")
urlpatterns = router.urls

urlpatterns += [
    path("webhook/plisio/", PlisioWebhookView.as_view(), name="webhook-plisio"),
    path("webhook/coingate/", CoinGateWebhookView.as_view(), name="webhook-coingate"),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
