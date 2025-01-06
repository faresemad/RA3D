import uuid

from django.conf import settings
from django.db import models
from django.db.models import TextChoices
from django.utils import timezone


class ReasonChoices(TextChoices):
    PAYMENT = "payment", "Payment"
    ITEM_PROBLEM = "item_problem", "Item Problem"
    REPORT_PROBLEM = "report_problem", "Report Problem"
    OTHER = "other", "Other"


class StatusChoices(TextChoices):
    OPENED = "opened", "Opened"
    CLOSED = "closed", "Closed"


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
