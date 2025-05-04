import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

User = get_user_model()


class CPanelType(models.TextChoices):
    CREATED = "Created", "Created"
    HACKED = "Hacked / Cracked", "Hacked / Cracked"


class CPanelStatus(models.TextChoices):
    SOLD = "Sold", "Sold"
    UNSOLD = "Unsold", "Unsold"
    DELETED = "Deleted", "Deleted"


class CPanel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cpanel")
    host = models.CharField(max_length=255, default="127.0.0.1")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    cpanel_type = models.CharField(max_length=255, choices=CPanelType.choices, default=CPanelType.CREATED)
    status = models.CharField(max_length=255, choices=CPanelStatus.choices, default=CPanelStatus.UNSOLD)
    ssl = models.BooleanField(default=False)
    tld = models.CharField(max_length=10, null=True, blank=True)
    hosting = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "cPanels"
        unique_together = ["host", "user"]
        indexes = [
            models.Index(fields=["host", "user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}'s cPanel {self.host}"

    @transaction.atomic
    def mark_as_delete(self) -> None:
        self.status = CPanelStatus.DELETED
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["status", "is_deleted", "deleted_at"])

    @transaction.atomic
    def mark_as_sold(self) -> None:
        self.status = CPanelStatus.SOLD
        self.save(update_fields=["status"])

    @transaction.atomic
    def mark_as_unsold(self) -> None:
        self.status = CPanelStatus.UNSOLD
        self.save(update_fields=["status"])
