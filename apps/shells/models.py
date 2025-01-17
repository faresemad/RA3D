import uuid

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone

User = get_user_model()


class ShellType(models.TextChoices):
    CREATED = "Created", "Created"
    HACKED = "Hacked / Cracked", "Hacked / Cracked"


class ShellStatus(models.TextChoices):
    SOLD = "Sold", "Sold"
    UNSOLD = "Unsold", "Unsold"
    DELETED = "Deleted", "Deleted"


class Shell(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shells")
    shell_url = models.URLField(max_length=355)
    shell_type = models.CharField(max_length=20, choices=ShellType.choices, default=ShellType.CREATED)
    status = models.CharField(max_length=20, choices=ShellStatus.choices, default=ShellStatus.UNSOLD)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Shells"
        unique_together = ["shell_url", "user"]
        indexes = [
            models.Index(fields=["shell_url", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s shell - {self.shell_url}"

    @transaction.atomic
    def mark_as_delete(self):
        self.status = ShellStatus.DELETED
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["status", "is_deleted", "deleted_at"])

    @transaction.atomic
    def mark_as_sold(self):
        self.status = ShellStatus.SOLD
        self.save(update_fields=["status"])

    @transaction.atomic
    def mark_as_unsold(self):
        self.status = ShellStatus.UNSOLD
        self.save(update_fields=["status"])

    @classmethod
    def get_user_shells(cls, user):
        return cls.objects.filter(user=user)

    @classmethod
    def get_by_status(cls, status):
        return cls.objects.filter(status=status)

    @classmethod
    def get_latest(cls, limit=10):
        return cls.objects.all()[:limit]
