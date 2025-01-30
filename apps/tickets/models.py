import uuid

from django.conf import settings
from django.db import models
from django.db.models import TextChoices
from django.utils import timezone


class ReasonChoices(TextChoices):
    PAYMENT = "Payment"
    ITEM_PROBLEM = "Item Problem"
    REPORT_PROBLEM = "Report Problem"
    OTHER = "Other"


class StatusChoices(TextChoices):
    OPENED = "Opened"
    CLOSED = "Closed"


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    title = models.CharField(max_length=255)
    reason = models.CharField(max_length=255, choices=ReasonChoices.choices)
    message = models.TextField()
    status = models.CharField(max_length=255, choices=StatusChoices.choices, default=StatusChoices.OPENED)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]

    def mark_as_opened(self):
        self.status = StatusChoices.OPENED
        self.save()

    def mark_as_closed(self):
        self.status = StatusChoices.CLOSED
        self.closed_at = timezone.now()
        self.save()


class TicketResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket.title} - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]
