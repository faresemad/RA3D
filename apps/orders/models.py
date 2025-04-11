import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import Account
from apps.cpanel.models import CPanel
from apps.rdp.models import Rdp
from apps.shells.models import Shell
from apps.wallet.models import Wallet

User = get_user_model()


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"


class PaymentMethod(models.TextChoices):
    BTC = "BTC", "Bitcoin"
    ETH = "ETH", "Ethereum"
    LTC = "LTC", "Litecoin"
    USDT = "USDT", "Tether"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    cpanel = models.ForeignKey(CPanel, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    rdp = models.ForeignKey(Rdp, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    shell = models.ForeignKey(Shell, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=255, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    cryptocurrency = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_price = 0
        if self.account:
            self.total_price += self.account.price
        if self.cpanel:
            self.total_price += self.cpanel.price
        if self.rdp:
            self.total_price += self.rdp.price
        if self.shell:
            self.total_price += self.shell.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}"

    def get_secret_data(self):
        pass

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
        ]


class Transaction(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    class Cryptocurrency(models.TextChoices):
        BTC = "BTC", "Bitcoin"
        ETH = "ETH", "Ethereum"
        LTC = "LTC", "Litecoin"
        USDT = "USDT", "Tether"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=255, unique=True)
    cryptocurrency = models.CharField(max_length=50, choices=Cryptocurrency.choices, default=Cryptocurrency.BTC)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    payment_status = models.CharField(max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.id}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["wallet"]),
        ]
