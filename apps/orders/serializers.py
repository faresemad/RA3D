import logging

from rest_framework import serializers

from apps.orders.helper.serializers import (
    AccountSerializer,
    CPanelSerializer,
    RdpSerializer,
    ShellSerializer,
    SMTPSerializer,
    WebMailSerializer,
)
from apps.orders.models import Order, PaymentMethod, Transaction
from apps.services.coingate import CoinGateService
from apps.services.order import ReservationService
from apps.services.transaction import TransactionService

coingate_service = CoinGateService()
logger = logging.getLogger(__name__)


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
            "smtp",
            "webmail",
            "total_price",
            "status",
            "cryptocurrency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_price", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        # Keep your existing validation
        if not any(
            [
                attrs.get("account"),
                attrs.get("cpanel"),
                attrs.get("rdp"),
                attrs.get("shell"),
                attrs.get("smtp"),
                attrs.get("webmail"),
            ]
        ):
            raise serializers.ValidationError("At least one product must be selected.")
        return attrs

    def create(self, validated_data):
        cryptocurrency = validated_data.pop("cryptocurrency")

        # Create the order first
        order = Order.objects.create(**validated_data, cryptocurrency=cryptocurrency)

        try:
            ReservationService.reserve_products(order)
        except ValueError as e:
            logger.error(f"Error reserving products: {e}")
            order.delete()
            raise serializers.ValidationError(str(e))

        # Now create the transaction using the service
        coingate_order = coingate_service.create_order(order, cryptocurrency)
        if not coingate_order:
            ReservationService._release_order_products(order)
            order.delete()
            logger.error("Failed to create order in CoinGate")
            raise serializers.ValidationError("Payment gateway error")

        TransactionService.create_transaction(order, coingate_order, cryptocurrency)
        return order


class ListOrderSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    cpanel = CPanelSerializer()
    rdp = RdpSerializer()
    shell = ShellSerializer()
    smtp = SMTPSerializer()
    webmail = WebMailSerializer()
    type_of_order = serializers.SerializerMethodField()

    class Meta:
        model = Order
        exclude = ["user"]

    def get_type_of_order(self, obj: Order) -> str:
        """Get the type of order based on the selected product."""
        if obj.account:
            return "account"
        elif obj.cpanel:
            return "cpanel"
        elif obj.rdp:
            return "rdp"
        elif obj.shell:
            return "shell"
        elif obj.smtp:
            return "smtp"
        elif obj.webmail:
            return "webmail"
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionHistorySerializer(serializers.ModelSerializer):
    order = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = ["id", "order", "cryptocurrency", "amount", "payment_status", "created_at"]
