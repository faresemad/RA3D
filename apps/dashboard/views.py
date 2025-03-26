from django.http import HttpRequest
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Account
from apps.cpanel.models import CPanel
from apps.orders.models import Order
from apps.rdp.models import Rdp
from apps.shells.models import Shell
from apps.smtp.models import SMTP
from apps.tickets.models import Ticket
from apps.wallet.models import Wallet
from apps.webmails.models import WebMail


class StatisticsViewSet(viewsets.ViewSet):
    """
    ViewSet for retrieving various dashboard statistics and user-specific information.

    Provides authenticated endpoints to fetch:
    - Total counts of system resources (accounts, cpanels, rdps, etc.)
    - User's wallet balance
    - User's ticket count
    - User's order count

    Requires authentication for all actions.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request: HttpRequest) -> Response:
        """Return the total count of system resources."""
        stats = {
            "accounts": Account.objects.count(),
            "cpanels": CPanel.objects.count(),
            "rdps": Rdp.objects.count(),
            "shells": Shell.objects.count(),
            "smtps": SMTP.objects.count(),
            "webmails": WebMail.objects.count(),
        }

        return Response(stats)

    @action(detail=False, methods=["get"])
    def wallet(self, request: HttpRequest) -> Response:
        """Return the balance of the authenticated user's wallet."""
        wallet = Wallet.objects.filter(user=request.user).first()
        return Response({"balance": wallet.get_balance() if wallet else 0})

    @action(detail=False, methods=["get"])
    def tickets(self, request: HttpRequest) -> Response:
        """Return the count of tickets for the authenticated user."""
        tickets = Ticket.objects.filter(user=request.user)
        return Response({"count": tickets.count()})

    @action(detail=False, methods=["get"])
    def orders(self, request: HttpRequest) -> Response:
        """Return the count of orders for the authenticated user."""
        orders = Order.objects.filter(user=request.user)
        return Response({"count": orders.count()})
