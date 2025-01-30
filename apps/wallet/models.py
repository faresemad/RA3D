import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}"

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def deposit(self, amount):
        self.balance += amount
        self.save()
        return True

    def transfer(self, wallet, amount):
        if self.withdraw(amount):
            wallet.deposit(amount)
            return True
        return False

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions.all()

    def get_transaction_count(self):
        return self.transactions.count()
