from rest_framework.routers import DefaultRouter

from apps.accounts.views import AccountCategoryViewSet, AccountDataViewSet, AccountViewSet

router = DefaultRouter()

app_name = "accounts"

router.register(r"accounts", AccountViewSet, basename="accounts")
router.register(r"account-data", AccountDataViewSet, basename="account-data")
router.register(r"account-category", AccountCategoryViewSet, basename="account-category")

urlpatterns = router.urls
