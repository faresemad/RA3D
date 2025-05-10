# services/wallet.py
import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.orders.models import Order
from apps.wallet.models import Wallet

logger = logging.getLogger(__name__)
User = get_user_model()


class WalletService:
    @staticmethod
    @transaction.atomic
    def get_wallet(user):
        """Get or create wallet with row-level locking"""
        wallet, created = Wallet.objects.select_for_update().get_or_create(user=user)
        return wallet

    @staticmethod
    @transaction.atomic
    def deposit(user, amount):
        """Atomic deposit operation with transaction logging"""
        wallet = WalletService.get_wallet(user)
        wallet.deposit(Decimal(amount))
        logger.info(f"Deposited {amount} to {user.email}'s wallet. New balance: {wallet.balance}")

    @staticmethod
    @transaction.atomic
    def withdraw(user, amount):
        """Atomic withdrawal with balance check"""
        wallet = WalletService.get_wallet(user)
        if wallet.withdraw(Decimal(amount)):
            logger.info(f"Withdrew {amount} from {user.email}'s wallet. New balance: {wallet.balance}")
            return True
        logger.error(f"Insufficient balance for withdrawal from {user.email}'s wallet")
        return False

    @staticmethod
    def get_transaction_history(wallet: Wallet):
        """Get transaction history for a user's wallet"""
        return wallet.get_transactions()

    @staticmethod
    def get_transaction_count(wallet):
        """Get transaction history for a user"""
        return wallet.get_transaction_count()

    @staticmethod
    def handle_order_completion(order: Order):
        """Credit seller wallet after successful order completion"""
        seller = None

        # Determine which product was purchased and get its owner
        if order.account:
            seller = order.account.user
        elif order.cpanel:
            seller = order.cpanel.user
        elif order.rdp:
            seller = order.rdp.user
        elif order.shell:
            seller = order.shell.user

        if not seller:
            logger.error(f"No seller found for order {order.id}")
            return

        try:
            WalletService.deposit(seller, order.total_price)
            logger.info(f"Credited {order.total_price} to seller {seller.email} for order {order.id}")
        except Exception as e:
            logger.error(f"Failed to credit seller for order {order.id}: {str(e)}")
            raise
        return seller
