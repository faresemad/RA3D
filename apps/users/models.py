import uuid
from datetime import timedelta
from random import randint

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.users.manager import UserManager


class CustomUserProfile(AbstractUser):
    class AccountStatus(models.TextChoices):
        SELLER = "SELLER", "Seller"
        PENDING_SELLER = "PENDING_SELLER", "Pending Seller"
        BUYER = "BUYER", "Buyer"
        SUPPORT = "SUPPORT", "Support"
        SUSPENDED = "SUSPENDED", "Suspended"
        SELLER_SUSPENDED = "SELLER_SUSPENDED", "Seller Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    new_email = models.EmailField(blank=True, null=True)
    picture = models.ImageField(upload_to="profile/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=AccountStatus.choices, default=AccountStatus.BUYER)
    id_document = models.CharField(blank=True, max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True, editable=False)
    suspended_until = models.DateTimeField(blank=True, null=True)
    is_lifelong_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def suspend(self, reason, duration_days=2):
        self.status = (
            self.AccountStatus.SELLER_SUSPENDED
            if self.status == self.AccountStatus.SELLER
            else self.AccountStatus.SUSPENDED
        )
        self.suspended_until = timezone.now() + timedelta(days=duration_days)
        self.suspension_reason = reason
        self.save()

    def suspend_lifetime(self, reason):
        self.status = (
            self.AccountStatus.SELLER_SUSPENDED
            if self.status == self.AccountStatus.SELLER
            else self.AccountStatus.SUSPENDED
        )
        self.suspended_until = None
        self.is_lifelong_suspended = True
        self.suspension_reason = reason
        self.save()

    def unsuspend(self):
        self.status = (
            self.AccountStatus.SELLER
            if self.status == self.AccountStatus.SELLER_SUSPENDED
            else self.AccountStatus.BUYER
        )
        self.suspended_until = None
        self.is_lifelong_suspended = False
        self.save()

    def is_suspended(self):
        return self.suspended_until is not None and timezone.now() < self.suspended_until


class ActivationCode(models.Model):
    user = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE)
    activation_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.code = randint(100000, 999999)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}"

    def create_activation_code(self):
        self.activation_code = randint(100000, 999999)
        self.save()
        return self.activation_code

    def verify_activation_code(self, code):
        if code == self.activation_code:
            self.user.email_confirmed = True
            self.user.save()
            return True
        return False
