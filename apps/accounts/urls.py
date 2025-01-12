from rest_framework.routers import DefaultRouter

from apps.accounts.views import AccountViewSet

router = DefaultRouter()

app_name = "accounts"

router.register(r"accounts", AccountViewSet, basename="accounts")

urlpatterns = router.urls
