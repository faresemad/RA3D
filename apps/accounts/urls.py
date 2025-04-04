from rest_framework.routers import DefaultRouter

from apps.accounts.views import AccountViewSet, CountryOfAccounts, SellerAccountViewSet

router = DefaultRouter()

app_name = "accounts"

router.register(r"seller/accounts", SellerAccountViewSet, basename="seller-accounts")
router.register(r"countries", CountryOfAccounts, basename="countries")
router.register(r"accounts", AccountViewSet, basename="accounts")

urlpatterns = router.urls
