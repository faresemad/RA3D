import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from apps.users.models import CustomUserProfile
from apps.wallet.models import Wallet


class SellerRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE, related_name="seller_request")
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
        self._update_seller_status(CustomUserProfile.AccountStatus.SELLER)
        self._create_wallet_for_seller()
        self.save(update_fields=["status"])

    def reject(self):
        self.status = self.Status.REJECTED
        self._update_seller_status(CustomUserProfile.AccountStatus.BUYER)
        self.save(update_fields=["status"])

    def _update_seller_status(self, status):
        self.user.status = status
        self.user.save()
        self.save()

    def _create_wallet_for_seller(self):
        try:
            Wallet.objects.get(user=self.user)
        except ObjectDoesNotExist:
            Wallet.objects.create(user=self.user)

    def delete(self, using=None, keep_parents=False):
        self.user.status = CustomUserProfile.AccountStatus.BUYER
        self.user.save()
        super().delete(using, keep_parents)
