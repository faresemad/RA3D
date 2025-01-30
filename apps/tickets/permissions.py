# permissions.py
from django.http import HttpRequest
from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request: HttpRequest, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsTicketParticipantOrStaff(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view):
        ticket_id = view.kwargs.get("ticket_pk")
        if not ticket_id:
            return False

        from .models import Ticket

        ticket = Ticket.objects.get(pk=ticket_id)
        return ticket.user == request.user or request.user.is_staff
