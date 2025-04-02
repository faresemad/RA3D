from rest_framework.routers import DefaultRouter

from apps.wallet.views import WalletViewSet, WithdrawalRequestViewSet

router = DefaultRouter()

app_name = "wallet"

router.register(r"wallet", WalletViewSet, basename="wallet")
router.register(r"withdrawal-requests", WithdrawalRequestViewSet, basename="withdrawal-requests")

urlpatterns = router.urls
