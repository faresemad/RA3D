from rest_framework.routers import DefaultRouter

from apps.wallet.views import WalletViewSet

router = DefaultRouter()

app_name = "wallet"

router.register(r"", WalletViewSet, basename="wallet")

urlpatterns = router.urls
