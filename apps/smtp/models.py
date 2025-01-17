import uuid

from django.contrib.auth import get_user_model
from django.db import models, transaction

User = get_user_model()


class SMTPType(models.TextChoices):
    CREATED = "Created", "Created"
    HACKED = "Hacked / Cracked", "Hacked / Cracked"


class SmtpStatus(models.TextChoices):
    SOLD = "Sold", "Sold"
    UNSOLD = "Unsold", "Unsold"
    DELETED = "Deleted", "Deleted"


class SMTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="smtp")
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    smtp_type = models.CharField(max_length=255, choices=SMTPType.choices)
    status = models.CharField(max_length=255, choices=SmtpStatus.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}@{self.ip}:{self.port}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SMTP"
        verbose_name_plural = "SMTPs"
        unique_together = ["ip", "port"]
        indexes = [
            models.Index(fields=["ip", "port"]),
            models.Index(fields=["username"]),
        ]

    @transaction.atomic()
    def mark_as_sold(self):
        self.status = SmtpStatus.SOLD
        self.save()

    @transaction.atomic()
    def mark_as_unsold(self):
        self.status = SmtpStatus.UNSOLD
        self.save()

    @transaction.atomic()
    def mark_as_deleted(self):
        self.status = SmtpStatus.DELETED
        self.is_deleted = True
        self.deleted_at = models.DateTimeField(auto_now=True)
        self.save()
