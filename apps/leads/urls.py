from rest_framework.routers import DefaultRouter

from apps.leads.views import LeadsCategoryViewSet, LeadsDataViewSet, LeadsViewSet

router = DefaultRouter()

app_name = "leads"

router.register(r"leads", LeadsViewSet, basename="leads")
router.register(r"leads-data", LeadsDataViewSet, basename="leads-data")
router.register(r"leads-category", LeadsCategoryViewSet, basename="leads-category")

urlpatterns = router.urls
