from rest_framework import serializers

from apps.orders.models import Order, PaymentMethod, Transaction
from apps.services.coingate import CoinGateService
from apps.services.transaction import TransactionService

coingate_service = CoinGateService()


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cryptocurrency = serializers.ChoiceField(choices=PaymentMethod.choices, write_only=True, required=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "account",
            "cpanel",
            "rdp",
            "shell",
            "total_price",
            "status",
            "cryptocurrency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_price", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        # Keep your existing validation
        if not any([attrs.get("account"), attrs.get("cpanel"), attrs.get("rdp"), attrs.get("shell")]):
            raise serializers.ValidationError("At least one product must be selected.")
        return attrs

    def create(self, validated_data):
        cryptocurrency = validated_data.pop("cryptocurrency")

        # Create the order first
        order = Order.objects.create(**validated_data, cryptocurrency=cryptocurrency)

        # Now create the transaction using the service
        coingate_order = coingate_service.create_order(order, cryptocurrency)
        if not coingate_order:
            order.delete()
            raise serializers.ValidationError("Payment gateway error")

        TransactionService.create_transaction(order, coingate_order, cryptocurrency)
        return order


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
