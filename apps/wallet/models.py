import logging
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

logger = logging.getLogger(__name__)


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}"

    def withdraw(self, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(amount)
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=self.id)
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()
                return True
        return False

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not isinstance(amount, Decimal):
            amount = Decimal(amount)
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=self.id)
            wallet.balance += amount
            wallet.save()
            return True

    def transfer(self, wallet, amount):
        with transaction.atomic():
            if self.withdraw(amount):
                wallet.deposit(amount)
                return True
        return False

    @property
    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions.all()

    def get_transaction_count(self):
        return self.transactions.count()


class WithdrawalRequest(models.Model):
    class PaymentMethod(models.TextChoices):
        BITCOIN = "BITCOIN", "Bitcoin"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="withdrawal_requests")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("10.0"))])
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BITCOIN)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["payment_method"]),
        ]

    def __str__(self):
        return f"Withdrawal {self.amount} by {self.user.username} via {self.get_payment_method_display()}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.validate_withdrawal()
        super().save(*args, **kwargs)

    def validate_withdrawal(self):
        """Validate the withdrawal based on payment method."""
        payment_method = self.payment_method
        amount = self.amount
        min_withdrawal, fee = self.get_min_withdrawal_and_fee(payment_method)

        if amount < min_withdrawal:
            raise ValidationError(f"Minimum withdrawal amount for {payment_method} is {min_withdrawal}.")

        # Check if user has sufficient balance after fees
        if amount + fee > self.user.wallet.balance:
            raise ValidationError(f"Insufficient funds after applying {fee} fee for {payment_method} withdrawal.")

    @classmethod
    def get_min_withdrawal_and_fee(cls, payment_method):
        """Return minimum withdrawal and fee based on the payment method."""
        if payment_method == cls.PaymentMethod.BITCOIN:
            return Decimal("100.0"), Decimal("20.0")  # Min withdrawal: 100, Fee: 20
        else:
            raise ValueError("Invalid payment method.")

    def approve(self):
        with transaction.atomic():
            withdrawal = WithdrawalRequest.objects.select_for_update().get(pk=self.pk)
            if withdrawal.status == self.Status.PENDING:
                withdrawal.status = self.Status.APPROVED
                withdrawal.save()

    def reject(self):
        with transaction.atomic():
            withdrawal = WithdrawalRequest.objects.select_for_update().get(pk=self.pk)
            if withdrawal.status == self.Status.PENDING:
                withdrawal.status = self.Status.REJECTED
                withdrawal.save()

    def _complete(self, transaction_id):
        logger.info(f"Attempting to complete withdrawal {self.id} with transaction ID {transaction_id}")
        with transaction.atomic():
            withdrawal = WithdrawalRequest.objects.select_for_update().get(pk=self.pk)
            if withdrawal.status != self.Status.APPROVED:
                logger.warning(f"Withdrawal {self.id} is not approved. Current status: {self.status}")
                return

            withdrawal.status = self.Status.COMPLETED
            withdrawal.transaction_id = transaction_id
            try:
                withdrawal.user.wallet.withdraw(withdrawal.amount)
                withdrawal.save()
                logger.info(f"Withdrawal {self.id} completed successfully.")
            except Exception as e:
                logger.error(f"Error completing withdrawal {self.id}: {e}")
                raise
