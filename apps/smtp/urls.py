from rest_framework.routers import DefaultRouter

from apps.smtp.views import LocationsOfSmtpViewSet, SellerSmtpViewSet, SmtpViewSet

router = DefaultRouter()

app_name = "smtp"

router.register(r"locations", LocationsOfSmtpViewSet, basename="smtp-locations")
router.register(r"seller/smtp", SellerSmtpViewSet, basename="seller-smtp")
router.register(r"smtp", SmtpViewSet, basename="smtp")

urlpatterns = router.urls
