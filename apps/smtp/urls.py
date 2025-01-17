from rest_framework.routers import DefaultRouter

from apps.smtp.views import SmtpViewSet

router = DefaultRouter()

app_name = "smtp"

router.register(r"smtp", SmtpViewSet, basename="smtp")

urlpatterns = router.urls
