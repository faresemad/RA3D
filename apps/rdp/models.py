import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

User = get_user_model()


class RdpType(models.TextChoices):
    CREATED = "Created", "Created"
    HACKED = "Hacked / Cracked", "Hacked / Cracked"


class RdpStatus(models.TextChoices):
    SOLD = "Sold", "Sold"
    UNSOLD = "Unsold", "Unsold"
    DELETED = "Deleted", "Deleted"


class RdpUserAccessType(models.TextChoices):
    ADMIN = "Admin", "Admin"
    USER = "User", "User"


class RdpWindowsType(models.TextChoices):
    WINDOWS = "Windows", "Windows"
    WIN_XP = "Win XP", "Win XP"
    WIN_VISTA = "Win Vista", "Win Vista"
    WIN_2003 = "Win 2003", "Win 2003"
    WIN_2008 = "Win 2008", "Win 2008"
    WIN_7 = "Win 7", "Win 7"
    WIN_8 = "Win 8", "Win 8"
    WIN_10 = "Win 10", "Win 10"
    WIN_SERVER_2012 = "Win Server 2012", "Win Server 2012"
    WIN_SERVER_2016 = "Win Server 2016", "Win Server 2016"
    WIN_SERVER_2019 = "Win Server 2019", "Win Server 2019"
    WIN_SERVER_2022 = "Win Server 2022", "Win Server 2022"
    WIN_SERVER_2025 = "Win Server 2025", "Win Server 2025"
    OTHER = "Other", "Other"


class Rdp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rdps")
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    ram_size = models.IntegerField(default=0)
    cpu_cores = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    rdp_type = models.CharField(max_length=255, choices=RdpType.choices, default=RdpType.CREATED)
    status = models.CharField(max_length=255, choices=RdpStatus.choices, default=RdpStatus.UNSOLD)
    windows_type = models.CharField(max_length=255, choices=RdpWindowsType.choices, default=RdpWindowsType.WINDOWS)
    access_type = models.CharField(max_length=255, choices=RdpUserAccessType.choices, default=RdpUserAccessType.USER)
    location = models.CharField(max_length=255, null=True, blank=True)
    hosting = models.CharField(max_length=255, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Rdps"
        unique_together = ["ip", "user"]
        indexes = [
            models.Index(fields=["ip", "user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}'s RDP {self.ip}"

    @transaction.atomic
    def mark_as_delete(self) -> None:
        self.status = RdpStatus.DELETED
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["status", "is_deleted", "deleted_at"])

    @transaction.atomic
    def mark_as_sold(self) -> None:
        self.status = RdpStatus.SOLD
        self.save(update_fields=["status"])

    @transaction.atomic
    def mark_as_unsold(self) -> None:
        self.status = RdpStatus.UNSOLD
        self.save(update_fields=["status"])

    @classmethod
    def get_user_rdps(cls, user) -> models.QuerySet:
        return cls.objects.filter(user=user, is_deleted=False)

    @classmethod
    def get_by_status(cls, status: str) -> models.QuerySet:
        return cls.objects.filter(status=status, is_deleted=False)

    @classmethod
    def get_latest(cls, limit: int = 10) -> models.QuerySet:
        return cls.objects.filter(is_deleted=False).order_by("-created_at")[:limit]
