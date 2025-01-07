from rest_framework.routers import DefaultRouter

from apps.business.views import BusinessCategoryViewSet, BusinessDataViewSet, BusinessViewSet

router = DefaultRouter()

app_name = "business"

router.register(r"business", BusinessViewSet, basename="business")
router.register(r"business-data", BusinessDataViewSet, basename="business-data")
router.register(r"business-category", BusinessCategoryViewSet, basename="business-category")

urlpatterns = router.urls
