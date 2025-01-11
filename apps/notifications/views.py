from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications/notification_list.html", {"notifications": notifications})


def create_notification(request):
    if request.method == "GET":
        message = "Create notification"
        notification = Notification.objects.create(user=request.user, message=message)
        return JsonResponse({"message": "Notification created!", "notification_id": str(notification.id)})
    return JsonResponse({"error": "Invalid request"}, status=400)
