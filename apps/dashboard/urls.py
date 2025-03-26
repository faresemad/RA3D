from rest_framework.routers import DefaultRouter

from apps.dashboard.views import StatisticsViewSet

router = DefaultRouter()

app_name = "dashboard"

router.register(r"statistics", StatisticsViewSet, basename="statistics")

urlpatterns = router.urls
