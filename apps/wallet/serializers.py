from rest_framework import serializers

from apps.users.api.serializers.profile import UserProfileSerializer
from apps.wallet.models import Wallet, WithdrawalRequest


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user", "balance", "created_at", "updated_at"]


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = WithdrawalRequest
        fields = [
            "user",
            "amount",
            "payment_method",
            "wallet_address",
        ]

    def validate_wallet_address(self, value):
        """
        Validate that the wallet address is a valid Bitcoin address.
        Basic validation checks for length and starting characters.
        """
        payment_method = self.initial_data.get("payment_method")
        if payment_method == "BITCOIN":
            if not value:
                raise serializers.ValidationError("Bitcoin wallet address is required.")

            # Basic Bitcoin address validation
            # Checks if address starts with valid prefixes and has correct length
            valid_prefixes = ("1", "3", "bc1")
            if not any(value.startswith(prefix) for prefix in valid_prefixes):
                raise serializers.ValidationError("Invalid Bitcoin address format.")

            if len(value) < 26 or len(value) > 35:
                raise serializers.ValidationError("Invalid Bitcoin address length.")

        return value

    def validate(self, data):
        user = data["user"]
        amount = data["amount"]
        payment_method = data["payment_method"]

        # Correct call to the class method
        min_withdrawal, fee = WithdrawalRequest.get_min_withdrawal_and_fee(payment_method)

        if amount < min_withdrawal:
            raise serializers.ValidationError(f"Minimum withdrawal for {payment_method} is {min_withdrawal}.")

        # Check if the user has sufficient funds after applying the fee
        if amount + fee > user.wallet.balance:
            raise serializers.ValidationError(
                f"Insufficient funds for withdrawal. Your current balance is {user.wallet.balance}."
            )

        return data


class WithdrawalRequestActionSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()


class WithdrawalRequestListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    payment_fee = serializers.SerializerMethodField()

    class Meta:
        model = WithdrawalRequest
        fields = [
            "id",
            "user",
            "amount",
            "payment_method",
            "wallet_address",
            "payment_fee",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]

    def get_payment_fee(self, obj: WithdrawalRequest):
        """Returns the fee for the withdrawal based on the payment method."""
        _, fee = WithdrawalRequest.get_min_withdrawal_and_fee(obj.payment_method)
        return fee
