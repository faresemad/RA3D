import uuid

from django.conf import settings
from django.db import models


class SellerRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_request")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    national_id = models.ImageField(upload_to="national_id/")
    created_at = models.DateTimeField(auto_now_add=True)
    admin_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    class Meta:
        verbose_name = "Seller Request"
        verbose_name_plural = "Seller Requests"
        ordering = ["-created_at"]

    def approve(self):
        self.status = self.Status.APPROVED
        self.user.status = self.user.AccountStatus.SELLER
        self.save()

    def reject(self, comment=None):
        self.status = self.Status.REJECTED
        self.admin_comment = comment
        self.user.status = self.user.AccountStatus.BUYER
        self.save()
