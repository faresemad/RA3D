from rest_framework.routers import DefaultRouter

from apps.tickets.views import TicketViewSet

router = DefaultRouter()

app_name = "tickets"

router.register(r"", TicketViewSet, basename="tickets")
urlpatterns = router.urls
