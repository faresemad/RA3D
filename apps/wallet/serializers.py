from rest_framework import serializers

from apps.wallet.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user", "balance", "created_at", "updated_at"]
