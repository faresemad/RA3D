from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from apps.tickets.views import TicketResponseViewSet, TicketViewSet

router = DefaultRouter()

app_name = "tickets"

router.register(r"tickets", TicketViewSet, basename="tickets")

tickets_router = routers.NestedSimpleRouter(router, r"tickets", lookup="ticket")
tickets_router.register(r"responses", TicketResponseViewSet, basename="ticket-responses")


urlpatterns = router.urls + tickets_router.urls
